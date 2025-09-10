from common_components.configurations.singlethon_basic_config import SingletonBasicConfig
from pydantic_settings import SettingsConfigDict
from typing import Optional


class JWTConfig(SingletonBasicConfig):
    """JWT configuration loaded from environment variables.

    Supports both symmetric (HS256) and asymmetric (RS256) algorithms.
    For RS256, both private and public keys are required.
    """
    model_config = SettingsConfigDict(env_prefix="JWT_")
    algo: str
    exp_sec: int
    key: str
    public_key: Optional[str] = None
    kid: Optional[str] = None
    jwks_exp: int = 600
