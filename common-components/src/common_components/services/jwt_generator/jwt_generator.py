import jwt as pyjwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Annotated
from fastapi import Depends
from cryptography.hazmat.primitives import serialization
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
    def generate_token(cls, data: dict[str, Any], key: str, algorithm: str, expiration: int,
                       headers: dict[str, Any] | None = None) -> JWTTokenResponse:
        """Generate a JWT token with the provided parameters.

        Args:
            data: The payload data to include in the JWT token
            key: The signing key for the JWT token
            algorithm: The algorithm to use for signing (e.g., 'HS256', 'RS256')
            expiration: The expiration time in seconds from now
            headers: Optional additional headers to include in the JWT (e.g., kid)

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

            # Process key for RSA algorithms
            signing_key = cls._process_key_for_signing(key, algorithm)

            # Generate the token with optional headers
            token = pyjwt.encode(payload, signing_key, algorithm=algorithm, headers=headers)

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
            # Process key for RSA algorithms
            verification_key = cls._process_key_for_verification(key, algorithm)

            decoded_payload = pyjwt.decode(token, verification_key, algorithms=[algorithm])
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

    @classmethod
    def _process_key_for_signing(cls, key: str, algorithm: str):
        """Process key for JWT signing based on algorithm.

        Args:
            key: Raw key string
            algorithm: JWT algorithm

        Returns:
            Processed key for PyJWT
        """
        if algorithm.startswith('RS'):
            # RSA algorithm - parse PEM private key
            try:
                # Handle escaped newlines from environment variables
                key_pem = key.replace('\\n', '\n')
                return serialization.load_pem_private_key(
                    key_pem.encode(),
                    password=None
                )
            except Exception as e:
                cls.logger.error(f"Failed to load RSA private key: {e}")
                raise ValueError(f"Invalid RSA private key: {e}")
        else:
            # HMAC algorithm - use key as-is
            return key

    @classmethod
    def _process_key_for_verification(cls, key: str, algorithm: str):
        """Process key for JWT verification based on algorithm.

        Args:
            key: Raw key string (public key for RSA, symmetric key for HMAC)
            algorithm: JWT algorithm

        Returns:
            Processed key for PyJWT verification
        """
        if algorithm.startswith('RS'):
            # RSA algorithm - parse PEM public key
            try:
                key_pem = key.replace('\\n', '\n')
                return serialization.load_pem_public_key(key_pem.encode())
            except Exception as e:
                cls.logger.error(f"Failed to load RSA public key: {e}")
                raise ValueError(f"Invalid RSA public key: {e}")
        else:
            # HMAC algorithm - use key as-is
            return key


async def get_jwt_generator() -> JWTGenerator:
    """Dependency function to get the JWTGenerator instance.

    Returns:
        JWTGenerator instance ready for use
    """
    return JWTGenerator()


JWTGeneratorDep = Annotated[JWTGenerator, Depends(get_jwt_generator)]
