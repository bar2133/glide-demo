from pydantic import BaseModel
from typing import Optional


class JWTEncryptionData(BaseModel):
    """JWT encryption configuration data.

    Contains the necessary information for JWT token signing and verification.
    Supports both symmetric (HMAC) and asymmetric (RSA/ECDSA) algorithms.
    """
    key: str
    algo: str
    exp_sec: int
    public_key: Optional[str] = None
    kid: Optional[str] = None  # Key ID for JWKS
