from common_components.configurations.singlethon_basic_config import SingletonBasicConfig
from pydantic_settings import SettingsConfigDict


class JWTConfig(SingletonBasicConfig):
    model_config = SettingsConfigDict(env_prefix="JWT_")
    algo: str
    exp_sec: int
    key: str
