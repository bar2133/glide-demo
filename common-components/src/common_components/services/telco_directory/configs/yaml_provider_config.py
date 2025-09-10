from common_components.services.telco_directory.configs.td_provider import TDProviderConfig
from pydantic_settings import SettingsConfigDict


class TDYamlConfig(TDProviderConfig):
    """Configuration for the YAML provider of the Telco Directory service.

    This configuration class defines the path to the YAML file and the hot reload
    and reload interval for the YAML provider.
    """
    model_config = SettingsConfigDict(env_prefix="TD_YAML_")
    path: str
    hot_reload: bool = False
    reload_interval: int = 5
