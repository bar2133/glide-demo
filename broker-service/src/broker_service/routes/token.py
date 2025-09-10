from common_components.server.routes.abstract_router import AbstractRouter
from common_components.models.telecom_dto import TelecomIdentifierDTO
from typing import Annotated
from fastapi import Query
from common_components.services.telco_directory.telco_directory import TelcoDirectoryDep
from fastapi import HTTPException
from common_components.services.redis.redis import RedisDep
from fastapi import Form
import httpx
from common_components.services.telco_directory.models.td_data import SingleTelcoData
from common_components.models.token import TokenDTO
from common_components.utils.consts.telco import TelcoConsts
from common_components.services.jwt_generator.jwt_generator import JWTGeneratorDep
from common_components.services.redis.enums.key_types import CacheKeyType
import asyncio
from common_components.services.secret_manger.secret_manager import SecretManagerDep
from common_components.models.oauth_enums import GrantType
import json


class ContactTelcoAndGenerateToken(AbstractRouter):
    """Contact telco and generate token router."""

    def register_routes(self):
        self.router.post("/token")(self.token_request)

    @classmethod
    async def token_request(cls,
                            telecom_dto: Annotated[TelecomIdentifierDTO, Query()],
                            auth_code: Annotated[str, Form()],
                            telco_directory: TelcoDirectoryDep,
                            secret_manager: SecretManagerDep,
                            jwt_generator: JWTGeneratorDep,
                            redis: RedisDep) -> TokenDTO:
        """Handle OAuth token generation request by acting as a broker between clients and telco services.

        This method implements a two-step token generation process:
        1. First, it forwards the request to the appropriate telco service to obtain a telco-specific token
        2. Then, it generates its own broker token using JWT encryption

        The method includes Redis caching to improve performance by storing both telco and broker tokens.
        It uses the telco directory service to route requests to the correct telco service based on MCC/SN prefix matching.

        Args:
            telecom_dto: The telecom identifier containing MCC (Mobile Country Code) and SN (Service Number).
            auth_code: The OAuth authorization code received from the form data.
            telco_directory: Dependency for telco directory service that provides routing information.
            secret_manager: Dependency for secret manager service that provides JWT encryption keys.
            jwt_generator: Dependency for JWT token generation service.
            redis: Dependency for Redis caching service (optional).

        Returns:
            TokenDTO: A broker token containing access_token, grant_type, issued_at, and expiration times.

        Raises:
            HTTPException:
                - 400: If telco data is not found for the given MCC/SN combination
                - 503: If the telco service is unreachable
                - 500: If an unexpected error occurs during token generation
        """
        if redis and (res := await redis.get_value(redis.get_key(CacheKeyType.BROKER_TOKEN, telecom_dto))):
            cls.logger.info(f"Broker token found in redis: {res}")
            return TokenDTO.model_validate_json(res)

        # Get telco data based on MCC
        telco_data = await telco_directory.get_telco_data(telecom_dto.mcc, telecom_dto.sn)
        if not telco_data:
            raise HTTPException(status_code=400, detail="Destination Telco data not found")

        telco_token = await cls.get_telco_token(telecom_dto, telco_data, auth_code)
        asyncio.create_task(cls.save_token_to_redis(redis, telecom_dto, CacheKeyType.TELECOM_TOKEN, telco_token))

        broker_token = cls.generate_broker_token(telecom_dto, auth_code, secret_manager, jwt_generator)
        asyncio.create_task(cls.save_token_to_redis(redis, telecom_dto, CacheKeyType.BROKER_TOKEN, broker_token))

        return broker_token

    @classmethod
    def _build_package_request(
            cls,
            telecom_dto: TelecomIdentifierDTO,
            telco_data: SingleTelcoData,
            auth_code: str) -> dict:
        """Build the HTTP request package for forwarding to telco service.

        Constructs the complete request structure including target URL, form data with telco authentication,
        and query parameters needed for the telco service token generation endpoint.

        Args:
            telecom_dto: The telecom identifier containing MCC and SN for query parameters.
            telco_data: The telco service configuration containing base_url, client_id, and client_secret.
            auth_code: The OAuth authorization code to be forwarded to the telco service.

        Returns:
            dict: A dictionary containing:
                - target_url: Complete URL for the telco service token endpoint
                - form_data: Dictionary with JSON-serialized telco_auth credentials and auth_code
                - query_params: Dictionary with MCC and SN parameters
        """
        # Forward the request to the telco service
        target_url = f"{telco_data.base_url}/api/demo/token"
        telco_auth = {"client_id": telco_data.client_id, "client_secret": telco_data.client_secret}
        return {
            "target_url": target_url,
            "form_data": {
                "telco_auth": json.dumps(telco_auth),
                "auth_code": auth_code
            },
            "query_params": {
                TelcoConsts.MCC: telecom_dto.mcc,
                TelcoConsts.SN: telecom_dto.sn
            }
        }

    @classmethod
    async def get_telco_token(cls, telecom_dto: TelecomIdentifierDTO, telco_data: SingleTelcoData,
                              auth_code: str) -> TokenDTO:
        """Forward token generation request to the appropriate telco service and return the response.

        This method handles the HTTP communication with telco services, including proper error handling
        and timeout management. It constructs the request using telco-specific authentication credentials
        and forwards the authorization code along with telecom identifiers.

        Args:
            telecom_dto: The telecom identifier containing MCC and SN for the request.
            telco_data: The telco service configuration with base_url and authentication credentials.
            auth_code: The OAuth authorization code to be forwarded to the telco service.

        Returns:
            TokenDTO: The token response from the telco service containing access_token and metadata.

        Raises:
            HTTPException:
                - Status code from telco service: If telco service returns an HTTP error
                - 503: If the telco service is unreachable or connection fails
                - 500: If an unexpected error occurs during the HTTP request
        """
        try:
            async with httpx.AsyncClient() as client:
                package_request = cls._build_package_request(telecom_dto, telco_data, auth_code)
                cls.logger.info(f"Forwarding request to {package_request['target_url']}")
                response = await client.post(
                    package_request['target_url'],
                    data=package_request['form_data'],
                    params=package_request['query_params'],
                    timeout=30.0
                )

                # Check if the request was successful
                response.raise_for_status()

                # Return the JSON response from the telco service
                return TokenDTO(**response.json())

        except httpx.HTTPStatusError as e:
            cls.logger.error(f"HTTP error when forwarding to telco service: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Telco service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            cls.logger.error(f"Request error when forwarding to telco service: {e}")
            raise HTTPException(
                status_code=503,
                detail="Failed to contact telco service"
            )
        except Exception as e:
            cls.logger.error(f"Unexpected error when forwarding to telco service: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    @classmethod
    async def save_token_to_redis(cls, redis: RedisDep, telecom_dto: TelecomIdentifierDTO,
                                  token_type: CacheKeyType, token: TokenDTO) -> None:
        """Save a token to Redis cache with automatic expiration based on token lifetime.

        This method stores tokens in Redis using a structured key format and sets the expiration
        time to match the token's natural expiration. This ensures cached tokens are automatically
        cleaned up and prevents serving expired tokens from cache.

        Args:
            redis: The Redis service dependency (optional, method returns silently if None).
            telecom_dto: The telecom identifier used to generate the cache key.
            token_type: The type of token being cached (BROKER_TOKEN or TELECOM_TOKEN).
            token: The token object to be cached, containing expiration information.

        Returns:
            None: This method performs an asynchronous side effect and returns nothing.

        Note:
            The method calculates expiration time as the difference between token.exp and token.iat
            to ensure the cached token expires at the same time as the actual token.
        """
        if redis:
            key = redis.get_key(token_type, telecom_dto)
            await redis.set_value(key=key,
                                  value=token.model_dump_json(),
                                  exp_sec=int((token.exp - token.iat).total_seconds()))
            cls.logger.info(f"{token_type.value} token saved to redis with key: {key}")

    @classmethod
    def generate_broker_token(cls, telecom_dto: TelecomIdentifierDTO, auth_code: str,
                              secret_manager: SecretManagerDep, jwt_generator: JWTGeneratorDep) -> TokenDTO:
        """Generate a broker-specific JWT token containing telecom and authorization information.

        This method creates a broker token that encapsulates the telecom identifiers and authorization code
        in a JWT format. The token is signed using encryption keys and algorithms provided by the secret manager
        and includes standard OAuth claims like issued_at and expires_at timestamps.

        Args:
            telecom_dto: The telecom identifier containing MCC and SN to embed in the token payload.
            auth_code: The original authorization code to include in the token payload.
            secret_manager: Service dependency that provides JWT encryption keys and algorithm configuration.
            jwt_generator: Service dependency that handles the actual JWT token creation and signing.

        Returns:
            TokenDTO: A broker token with:
                - access_token: The signed JWT string
                - grant_type: Set to CLIENT_CREDENTIALS
                - iat: Token issued at timestamp
                - exp: Token expiration timestamp

        Note:
            The generated token includes MCC, SN, and auth_code in its payload and uses the
            encryption settings (key, algorithm, expiration) from the secret manager configuration.
        """
        cls.logger.info(f"Generating broker token for {telecom_dto.mcc} {telecom_dto.sn}")
        jwt_encryption_data = secret_manager.get_jwt_encryption_key()
        jwt_token = jwt_generator.generate_token(
            data={TelcoConsts.MCC: telecom_dto.mcc, TelcoConsts.SN: telecom_dto.sn, "auth_code": auth_code},
            key=jwt_encryption_data.key,
            algorithm=jwt_encryption_data.algo,
            expiration=jwt_encryption_data.exp_sec
        )
        cls.logger.info(f"Broker token generated: {jwt_token}")
        return TokenDTO(access_token=jwt_token.token,
                        grant_type=GrantType.CLIENT_CREDENTIALS,
                        iat=jwt_token.created_at,
                        exp=jwt_token.expires_at)
