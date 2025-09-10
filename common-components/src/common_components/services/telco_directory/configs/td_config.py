from common_components.configurations.singlethon_basic_config import SingletonBasicConfig
from common_components.services.telco_directory.enums.providers import TDProvidersTypes
from pydantic_settings import SettingsConfigDict


class TDConfig(SingletonBasicConfig):
    """Configuration for the Telco Directory service.

    This configuration class defines the provider type for the Telco Directory service,
    which determines the underlying data source for telco directory information.
    """
    model_config = SettingsConfigDict(env_prefix="TD_")
    provider: TDProvidersTypes
