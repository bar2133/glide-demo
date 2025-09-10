import jwt as pyjwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Annotated
from fastapi import Depends
from common_components.services.jwt_generator.models.jwt_token import (
    JWTTokenResponse
)
from common_components.configurations.singlethon_basic_config import Singleton


class JWTGenerator(metaclass=Singleton):
    """JWT generator service for creating and managing JSON Web Tokens.

    This service provides functionality to generate JWT tokens with customizable
    data, signing keys, algorithms, and expiration times.
    """

    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize the JWT generator service."""
        self.logger.info("JWT Generator service initialized")

    @classmethod
    def generate_token(cls, data: dict[str, Any], key: str, algorithm: str, expiration: int) -> JWTTokenResponse:
        """Generate a JWT token with the provided parameters.

        Args:
            data: The payload data to include in the JWT token
            key: The signing key for the JWT token
            algorithm: The algorithm to use for signing (e.g., 'HS256', 'RS256')
            expiration: The expiration time in seconds from now

        Returns:
            JWTTokenResponse containing the generated token and metadata

        Raises:
            ValueError: If the algorithm is not supported or parameters are invalid
            Exception: If token generation fails
        """
        try:
            # Calculate timestamps
            created_at = datetime.now(timezone.utc)
            expires_at = created_at + timedelta(seconds=expiration)

            # Prepare JWT payload
            payload = {
                **data,
                "iat": created_at,
                "exp": expires_at
            }

            # Generate the token
            token = pyjwt.encode(payload, key, algorithm=algorithm)

            cls.logger.info(f"JWT token generated successfully with algorithm: {algorithm}")

            return JWTTokenResponse(
                token=token,
                created_at=created_at,
                expires_at=expires_at,
                algorithm=algorithm
            )

        except pyjwt.InvalidKeyError as e:
            cls.logger.error(f"Invalid key provided for JWT generation: {e}")
            raise ValueError(f"Invalid signing key: {e}")
        except pyjwt.InvalidAlgorithmError as e:
            cls.logger.error(f"Invalid algorithm provided for JWT generation: {e}")
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        except Exception as e:
            cls.logger.error(f"Error generating JWT token: {e}")
            raise Exception(f"Token generation failed: {e}")

    @classmethod
    def decode_token(cls, token: str, key: str, algorithm: str) -> dict[str, Any]:
        """Verify and decode a JWT token.

        Args:
            token: The JWT token to verify
            key: The signing key used to verify the token
            algorithm: The algorithm used for verification

        Returns:
            The decoded payload data

        Raises:
            pyjwt.ExpiredSignatureError: If the token has expired
            pyjwt.InvalidTokenError: If the token is invalid
            pyjwt.InvalidSignatureError: If the signature is invalid
        """
        try:
            decoded_payload = pyjwt.decode(token, key, algorithms=[algorithm])
            cls.logger.info("JWT token verified successfully")
            return decoded_payload
        except pyjwt.ExpiredSignatureError as e:
            cls.logger.error(f"JWT token has expired: {e}")
            raise
        except pyjwt.InvalidSignatureError as e:
            cls.logger.error(f"JWT token has invalid signature: {e}")
            raise
        except pyjwt.InvalidTokenError as e:
            cls.logger.error(f"JWT token is invalid: {e}")
            raise


async def get_jwt_generator() -> JWTGenerator:
    """Dependency function to get the JWTGenerator instance.

    Returns:
        JWTGenerator instance ready for use
    """
    return JWTGenerator()


JWTGeneratorDep = Annotated[JWTGenerator, Depends(get_jwt_generator)]
