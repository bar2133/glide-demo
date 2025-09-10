import logging
from common_components.server.routes.abstract_router import AbstractRouter
from common_components.models.oauth_enums import GrantType
from common_components.models.token import TokenDTO
from common_components.services.secret_manger.secret_manager import SecretManagerDep
from common_components.services.jwt_generator.jwt_generator import JWTGeneratorDep
from typing import Annotated
from fastapi import Query, Form
from common_components.models.telecom_dto import TelecomIdentifierDTO
from fastapi import HTTPException
from common_components.services.redis.redis import RedisDep
import asyncio
from common_components.utils.consts.telco import TelcoConsts
from common_components.services.redis.enums.key_types import CacheKeyType


class TokensGenerator(AbstractRouter):
    logger: logging.Logger = logging.getLogger(__name__)

    def register_routes(self) -> None:
        """Register token generation routes."""
        self.router.post("/token")(self.handle_token_request)

    @classmethod
    async def handle_token_request(cls,
                                   telecom_dto: Annotated[TelecomIdentifierDTO, Query()],
                                   auth_code: Annotated[str, Form()],
                                   secret_manager: SecretManagerDep,
                                   jwt_generator: JWTGeneratorDep,
                                   redis: RedisDep) -> TokenDTO:
        """Generate a telco-specific OAuth access token with validation and caching.

        This method implements a telco service token generation endpoint that validates
        authorization codes, checks Redis cache for existing tokens, and generates new
        JWT tokens when needed.

        Args:
            telecom_dto: The telecom identifier containing MCC (Mobile Country Code) and SN (Service Number).
            auth_code: The OAuth authorization code that must contain "best_auth" for validation.
            secret_manager: Dependency for secret manager service that provides JWT encryption keys.
            jwt_generator: Dependency for JWT token generation service.
            redis: Dependency for Redis caching service (optional).

        Returns:
            TokenDTO: A telco token containing access_token, grant_type, issued_at, and expiration times.

        Raises:
            HTTPException:
                - 401: If the authorization code is invalid
        """
        cls.verfy_auth_code(auth_code)

        # check for token in redis
        if redis and (res := await cls.check_redis_token(redis, telecom_dto)):
            cls.logger.info(f"Token found in redis: {res}")
            return res

        # generate token
        token = cls.generate_token(telecom_dto, auth_code, secret_manager, jwt_generator)
        asyncio.create_task(cls.save_token_to_redis(redis, telecom_dto, token))
        return token

    @classmethod
    def verfy_auth_code(cls, auth_code: str) -> None:
        """Validate the authorization code according to telco service requirements.

        This method implements telco-specific authorization code validation logic.

        Args:
            auth_code: The authorization code to validate.

        Returns:
            None: Method returns nothing on successful validation.

        Raises:
            HTTPException: 401 status if the authorization code is invalid.
        """
        if not cls._check_auth_code(auth_code):
            cls.logger.error(f"Invalid auth code: {auth_code}")
            raise HTTPException(status_code=401, detail="Invalid auth code")

    @classmethod
    async def check_redis_token(cls, redis: RedisDep, telecom_dto: TelecomIdentifierDTO) -> TokenDTO | None:
        """Check Redis cache for an existing valid token for the given telecom identifier.

        This method attempts to retrieve a cached token from Redis using a structured key
        based on the telecom identifier. If found, it deserializes the JSON token data
        back into a TokenDTO object.

        Args:
            redis: The Redis service dependency (optional, returns None if not available).
            telecom_dto: The telecom identifier used to generate the cache key.

        Returns:
            TokenDTO: The cached token if found and valid, None otherwise.

        Note:
            The method relies on Redis key expiration to ensure only valid tokens are returned.
            Expired tokens are automatically removed by Redis TTL mechanism.
        """
        if redis and (res := await redis.get_value(redis.get_key(CacheKeyType.TELECOM_TOKEN, telecom_dto))):
            cls.logger.info(f"Token found in redis: {res}")
            return TokenDTO.model_validate_json(res)
        return None

    @classmethod
    def generate_token(cls, telecom_dto: TelecomIdentifierDTO, auth_code: str, secret_manager: SecretManagerDep,
                       jwt_generator: JWTGeneratorDep) -> TokenDTO:
        """Generate a new JWT token for the telco service with embedded telecom and auth information.

        This method creates a telco-specific JWT token containing the telecom identifiers and
        authorization code. The token is signed using encryption keys and algorithms from
        the secret manager.

        Args:
            telecom_dto: The telecom identifier containing MCC and SN to embed in token payload.
            auth_code: The validated authorization code to include in the token payload.
            secret_manager: Service dependency providing JWT encryption keys and configuration.
            jwt_generator: Service dependency handling JWT token creation and signing.

        Returns:
            TokenDTO: A new telco token with:
                - access_token: The signed JWT string
                - grant_type: Set to CLIENT_CREDENTIALS
                - iat: Token issued at timestamp
                - exp: Token expiration timestamp

        Note:
            The token payload includes MCC, SN, and auth_code claims, and uses encryption
            settings (key, algorithm, expiration) from the secret manager configuration.
        """
        cls.logger.info(f"Generating token for {telecom_dto.mcc} {telecom_dto.sn}")
        jwt_encryption_data = secret_manager.get_jwt_encryption_key()
        jwt_token = jwt_generator.generate_token(
            data={TelcoConsts.MCC: telecom_dto.mcc, TelcoConsts.SN: telecom_dto.sn, "auth_code": auth_code},
            key=jwt_encryption_data.key,
            algorithm=jwt_encryption_data.algo,
            expiration=jwt_encryption_data.exp_sec
        )
        cls.logger.info(f"Token generated: {jwt_token}")
        return TokenDTO(access_token=jwt_token.token,
                        grant_type=GrantType.CLIENT_CREDENTIALS,
                        iat=jwt_token.created_at,
                        exp=jwt_token.expires_at)

    @classmethod
    async def save_token_to_redis(cls, redis: RedisDep, telecom_dto: TelecomIdentifierDTO, token: TokenDTO) -> None:
        """Save the generated token to Redis cache with automatic expiration.

        This method stores the token in Redis using a structured key format and sets
        the expiration time to match the token's natural expiration, ensuring cached
        tokens are automatically cleaned up and preventing expired token serving.

        Args:
            redis: The Redis service dependency (optional, method returns silently if None).
            telecom_dto: The telecom identifier used to generate the cache key.
            token: The token object to be cached, containing expiration metadata.

        Returns:
            None: This method performs an asynchronous side effect and returns nothing.

        Note:
            Expiration time is calculated as the difference between token.exp and token.iat
            to ensure the cached token expires simultaneously with the actual token.
        """
        if redis:
            key = redis.get_key(CacheKeyType.TELECOM_TOKEN, telecom_dto)
            await redis.set_value(key=key,
                                  value=token.model_dump_json(),
                                  exp_sec=int((token.exp - token.iat).total_seconds()))
            cls.logger.info(f"Token saved to redis with key: {key}")

    @staticmethod
    def _check_auth_code(auth_code: str) -> bool:
        """Internal method to validate authorization code format and content.

        This method implements the core authorization code validation logic used by
        the telco service.

        Args:
            auth_code: The authorization code string to validate.

        Returns:
            bool: True if the authorization code is valid, False otherwise.

        Note:
            This is a simplified validation for demonstration purposes.
        """
        return "best_auth" in auth_code.lower()
