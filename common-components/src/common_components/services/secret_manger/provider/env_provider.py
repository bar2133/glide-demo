from common_components.services.secret_manger.provider.abs_provider import SMProvider
from common_components.services.secret_manger.enums.providers import SMProvidersTypes
from common_components.services.secret_manger.configs.sm_provider_config import SMProviderConfig
from common_components.services.secret_manger.models.jwt_encryption import JWTEncryptionData
from common_components.services.secret_manger.configs.jwt_config import JWTConfig


class EnvProvider(SMProvider):
    """Environment-based secret management provider.

    This provider loads JWT encryption configuration from environment variables using
    the JWTConfig class. It implements the SMProvider interface to provide JWT encryption
    data sourced from environment variables with the JWT_ prefix.

    The provider automatically registers itself with the SMProviderFactory as the
    ENVIRONMENT provider type and uses SMProviderConfig as its configuration type.
    """
    provider_type = SMProvidersTypes.ENVIRONMENT
    config_type = SMProviderConfig

    async def load(self) -> None:
        """Load JWT encryption configuration from environment variables.

        Loads JWT configuration using JWTConfig which reads environment variables
        with the JWT_ prefix. The loaded configuration is stored as JWTEncryptionData
        in the data attribute and the loaded flag is set to True.

        Raises:
            Exception: If there's an error loading the JWT configuration from
                environment variables. The original exception is logged and re-raised.
        """
        try:
            jwt_config = JWTConfig()
        except Exception as e:
            self.logger.error(f"Error loading JWT config: {e}")
            raise e
        self.data = JWTEncryptionData(
            key=jwt_config.key,
            algo=jwt_config.algo,
            exp_sec=jwt_config.exp_sec)
        self.loaded = True

    def _get_jwt_encryption_key(self) -> JWTEncryptionData:
        """Extract JWT encryption key from loaded environment data.

        Returns the JWTEncryptionData that was loaded from environment variables
        during the load() method execution. This method assumes the provider has
        already been loaded and contains valid data.

        Returns:
            JWTEncryptionData: The JWT encryption configuration containing key,
                algorithm, and expiration time loaded from environment variables.
        """
        return self.data
