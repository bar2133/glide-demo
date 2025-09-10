from common_components.configurations.singlethon_basic_config import SingletonBasicConfig
from pydantic_settings import SettingsConfigDict


class TelcoAuthConfig(SingletonBasicConfig):
    """Telco authentication configuration loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_prefix="TELECOM_AUTH_")
    client_id: str
    client_secret: str
