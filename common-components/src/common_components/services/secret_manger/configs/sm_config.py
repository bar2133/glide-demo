from common_components.configurations.singlethon_basic_config import SingletonBasicConfig
from common_components.services.secret_manger.enums.providers import SMProvidersTypes
from pydantic_settings import SettingsConfigDict


class SMConfig(SingletonBasicConfig):
    model_config = SettingsConfigDict(env_prefix="SM_")
    provider: SMProvidersTypes
