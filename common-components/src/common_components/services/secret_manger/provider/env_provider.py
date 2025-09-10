from common_components.services.secret_manger.provider.abs_provider import SMProvider
from common_components.services.secret_manger.enums.providers import SMProvidersTypes
from common_components.services.secret_manger.configs.sm_provider_config import SMProviderConfig
from common_components.services.secret_manger.models.jwt_encryption import JWTEncryptionData
from common_components.services.secret_manger.configs.jwt_config import JWTConfig
from common_components.services.secret_manger.configs.telco_auth import TelcoAuthConfig
from common_components.services.secret_manger.models.telco_auth import TelcoAuthData


class EnvProvider(SMProvider):
    """Environment-based secret management provider.

    This provider loads JWT encryption configuration from environment variables using
    the JWTConfig class. It supports both symmetric (HMAC) and asymmetric (RSA) algorithms.
    """
    provider_type = SMProvidersTypes.ENVIRONMENT
    config_type = SMProviderConfig

    async def load(self) -> None:
        """Load JWT encryption configuration from environment variables.

        Loads JWT configuration using JWTConfig which reads environment variables
        with the JWT_ prefix. Supports both symmetric and asymmetric key configurations.

        Raises:
            Exception: If there's an error loading the JWT configuration from
                environment variables.
        """
        self.data = {}
        self.loaded = True

    def get_jwt_encryption_key(self) -> JWTEncryptionData:
        """Get JWT encryption key data with automatic loading verification.

        This method ensures the provider is loaded before attempting to retrieve
        the JWT encryption key. The @loaded_first decorator validates that the
        provider has been loaded and has data available before proceeding.

        Returns:
            JWTEncryptionData: The JWT encryption key data from the provider.
        """
        try:
            jwt_config = JWTConfig()
            return JWTEncryptionData(
                key=jwt_config.key,
                algo=jwt_config.algo,
                exp_sec=jwt_config.exp_sec,
                public_key=jwt_config.public_key,
                kid=jwt_config.kid or None,
                jwks_exp=jwt_config.jwks_exp
            )
        except Exception as e:
            self.logger.error(f"Error loading JWT config: {e}")
            raise e

    def get_telco_auth(self) -> TelcoAuthData:
        try:
            telco_auth_config = TelcoAuthConfig()
            return TelcoAuthData(
                auth_client_certs=telco_auth_config.client_certs
            )
        except Exception as e:
            self.logger.error(f"Error loading Telco auth config: {e}")
            raise e
