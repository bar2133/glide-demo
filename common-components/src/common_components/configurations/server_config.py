from pydantic_settings import SettingsConfigDict
from .singlethon_basic_config import SingletonBasicConfig


class ServerConfig(SingletonBasicConfig):
    model_config = SettingsConfigDict(env_prefix="API_")
    name: str = ""
    port: int = 8001
    host: str = "0.0.0.0"
    hot_reload: bool = True
    version: str = "demo"
