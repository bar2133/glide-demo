from common_components.configurations.singlethon_basic_config import SingletonBasicConfig
from pydantic_settings import SettingsConfigDict


class RedisConfig(SingletonBasicConfig):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    enable: bool = False
    host: str = ""
    port: int = -1
    password: str = ""
    db: int = 0
