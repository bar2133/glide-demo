import logging
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from common_components.server.routes.abstract_router import AbstractRouter
from common_components.services.secret_manger.secret_manager import SecretManagerDep
from common_components.services.redis.redis import RedisDep
from fastapi import HTTPException
from typing import Dict, Any


class JWKSExporter(AbstractRouter):
    """JWKS exporter service for serving JSON Web Key Sets.

    This service provides the /.well-known/jwks.json endpoint that returns
    the JSON Web Key Set (JWKS) used for JWT token verification.
    Supports both RSA (recommended) and HMAC algorithms.
    """
    logger: logging.Logger = logging.getLogger(__name__)

    # Cache TTL for JWKS in seconds (24 hours)
    JWKS_CACHE_TTL = 86400

    def register_routes(self) -> None:
        """Register JWKS routes."""
        self.router.get("/.well-known/jwks.json")(self.handle_jwks_request)

    async def handle_jwks_request(self, redis: RedisDep, secret_manager: SecretManagerDep) -> Dict[str, Any]:
        """Handle GET request for /.well-known/jwks.json endpoint.

        Returns the JSON Web Key Set containing public key information
        for JWT token verification.

        Args:
            redis: Redis service dependency for caching.
            secret_manager: Secret manager dependency for JWT configuration.

        Returns:
            Dict containing the JWKS structure with public key metadata.

        Raises:
            HTTPException: If JWKS generation fails.
        """
        try:
            # Check cache first
            if redis:
                cached_jwks = await redis.get_value("jwks:public")
                if cached_jwks:
                    self.logger.info("Returning cached JWKS")
                    return json.loads(cached_jwks)

            # Generate fresh JWKS
            self.logger.info("Generating fresh JWKS")
            jwks = await self._generate_jwks(secret_manager)

            # Cache the result
            if redis:
                await redis.set_value(
                    key="jwks:public",
                    value=json.dumps(jwks),
                    exp_sec=self.JWKS_CACHE_TTL
                )

            return jwks

        except Exception as e:
            self.logger.error(f"Error handling JWKS request: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve JWKS")

    async def _generate_jwks(self, secret_manager: SecretManagerDep) -> Dict[str, Any]:
        """Generate JWKS structure from secret manager configuration.

        Creates a JSON Web Key Set containing public key information.
        Supports RSA (RS256) and HMAC (HS256) algorithms.

        Args:
            secret_manager: Secret manager dependency for JWT configuration.

        Returns:
            Dict containing the JWKS structure.

        Raises:
            Exception: If secret manager is not available or key processing fails.
        """
        if not secret_manager:
            raise Exception("Secret manager not available")

        # Get JWT encryption data
        jwt_encryption_data = secret_manager.get_jwt_encryption_key()

        if jwt_encryption_data.algo.startswith('RS'):
            # RSA algorithm - include public key in JWKS
            return await self._generate_rsa_jwks(jwt_encryption_data)
        elif jwt_encryption_data.algo.startswith('HS'):
            # HMAC algorithm - only metadata (no secret key exposure)
            return self._generate_hmac_jwks(jwt_encryption_data)
        else:
            raise Exception(f"Unsupported algorithm: {jwt_encryption_data.algo}")

    async def _generate_rsa_jwks(self, jwt_encryption_data) -> Dict[str, Any]:
        """Generate JWKS for RSA algorithms.

        Args:
            jwt_encryption_data: JWT encryption configuration.

        Returns:
            Dict containing RSA JWKS structure.
        """
        try:
            # Load the public key
            if jwt_encryption_data.public_key:
                public_key_pem = jwt_encryption_data.public_key
            else:
                # Extract public key from private key
                private_key = serialization.load_pem_private_key(
                    jwt_encryption_data.key.encode(),
                    password=None
                )
                public_key = private_key.public_key()
                public_key_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()

            # Load public key for JWKS formatting
            public_key = serialization.load_pem_public_key(public_key_pem.encode())

            if isinstance(public_key, rsa.RSAPublicKey):
                public_numbers = public_key.public_numbers()

                # Convert to base64url encoding
                def int_to_base64url(val):
                    val_bytes = val.to_bytes((val.bit_length() + 7) // 8, 'big')
                    return base64.urlsafe_b64encode(val_bytes).decode().rstrip('=')

                jwks = {
                    "keys": [
                        {
                            "kty": "RSA",
                            "use": "sig",
                            "alg": jwt_encryption_data.algo,
                            "kid": jwt_encryption_data.kid or "default_key_id",
                            "n": int_to_base64url(public_numbers.n),
                            "e": int_to_base64url(public_numbers.e),
                        }
                    ]
                }

                self.logger.info(f"Generated RSA JWKS with algorithm: {jwt_encryption_data.algo}")
                return jwks
            else:
                raise Exception("Public key is not an RSA key")

        except Exception as e:
            self.logger.error(f"Error generating RSA JWKS: {e}")
            raise

    def _generate_hmac_jwks(self, jwt_encryption_data) -> Dict[str, Any]:
        """Generate JWKS for HMAC algorithms.

        Note: For HMAC algorithms, we don't include the actual key value
        as it's a shared secret that should not be exposed publicly.

        Args:
            jwt_encryption_data: JWT encryption configuration.

        Returns:
            Dict containing HMAC JWKS structure (metadata only).
        """
        jwks = {
            "keys": [
                {
                    "kty": "oct",  # Key type: octet sequence (for HMAC)
                    "use": "sig",  # Usage: signature
                    "alg": jwt_encryption_data.algo,  # Algorithm (e.g., HS256)
                    "kid": jwt_encryption_data.kid or "default_key_id",
                    # Note: 'k' parameter (key value) is intentionally omitted for security
                }
            ]
        }

        self.logger.info(f"Generated HMAC JWKS with algorithm: {jwt_encryption_data.algo}")
        return jwks
