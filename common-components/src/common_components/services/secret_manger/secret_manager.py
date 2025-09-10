from common_components.services.secret_manger.configs.sm_config import SMConfig
from common_components.services.secret_manger.models.jwt_encryption import JWTEncryptionData
from common_components.services.secret_manger.provider.provider_factory import SMProviderFactory
import logging
from typing import Annotated
from fastapi import Depends


class SecretManager:
    """Service for managing secrets and encryption keys through configurable providers.

    The SecretManager acts as a facade for different secret management providers,
    allowing the application to retrieve sensitive information like JWT encryption
    keys through a unified interface. The actual provider implementation is
    determined by configuration and created using the SMProviderFactory.

    The service supports asynchronous loading of provider data and provides
    logging for monitoring secret management operations.
    """
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize the secret manager with configuration and provider setup.

        Creates a new SecretManager instance by loading the SMConfig configuration
        and instantiating the appropriate provider through the SMProviderFactory.
        If provider initialization fails, the error is logged and re-raised.

        Raises:
            Exception: If provider initialization fails, the original exception
                      is re-raised after logging the error.
        """
        self.config = SMConfig()
        try:
            self.provider = SMProviderFactory.get_provider(self.config.provider)
        except Exception as e:
            self.logger.error(f"Error initializing secret manager: {e}")
            raise e

    async def load(self):
        """Asynchronously load the secret provider data.

        Initializes the underlying provider by calling its load method if a provider
        is available. This method logs the loading process including the provider
        type being used and completion status.

        The load operation is provider-specific and may involve reading from
        external sources, files, or environment variables depending on the
        configured provider type.
        """
        if self.provider:
            self.logger.info(f"Loading secret manager with {self.provider.provider_type}")
            await self.provider.load()
            self.logger.info(f"Secret manager loaded successfully with {self.provider.provider_type}")

    def get_jwt_encryption_key(self) -> JWTEncryptionData:
        """Retrieve JWT encryption configuration from the provider.

        Fetches the JWT encryption data including the encryption key, algorithm,
        and expiration time from the configured secret provider. This method
        logs the retrieval operation for monitoring purposes.

        Returns:
            JWTEncryptionData: Object containing the JWT encryption key, algorithm,
                              and expiration time in seconds.

        Raises:
            AttributeError: If the provider is not properly initialized.
            Any provider-specific exceptions during key retrieval.
        """
        self.logger.info(f"Getting JWT encryption key from {self.provider.provider_type}")
        return self.provider.get_jwt_encryption_key()


async def get_secret_manager() -> SecretManager:
    """FastAPI dependency function to create and initialize a SecretManager instance.

    Creates a new SecretManager instance and ensures it is properly loaded
    before returning it. This function is designed to be used as a FastAPI
    dependency to inject a ready-to-use SecretManager into route handlers.

    Returns:
        SecretManager: A fully initialized and loaded SecretManager instance.

    Raises:
        Exception: If SecretManager initialization or loading fails.
    """
    secret_manager = SecretManager()
    await secret_manager.load()
    return secret_manager


SecretManagerDep = Annotated[SecretManager, Depends(get_secret_manager)]
