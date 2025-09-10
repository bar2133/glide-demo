from common_components.utils.metaclasses.singlethon import Singleton
from common_components.services.telco_directory.providers.abs_provider import TDProvider
from common_components.services.telco_directory.models.td_data import SingleTelcoData
import logging
from common_components.services.telco_directory.providers.provider_factory import TDProviderFactory
from common_components.services.telco_directory.configs.td_config import TDConfig
from typing import Annotated
from fastapi import Depends


class TelcoDirectory(metaclass=Singleton):
    """Singleton service for managing telco directory operations.

    This class provides a centralized interface for telco directory operations including
    loading, reloading, updating, and querying telco data. It uses a configurable provider
    system to support different data sources and implements the Singleton pattern to ensure
    a single instance throughout the application lifecycle.

    The service automatically configures itself based on the TD_PROVIDER environment variable
    and provides async methods for all operations to support non-blocking I/O operations.
    """
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize the TelcoDirectory singleton instance.

        Creates configuration from environment variables and initializes the appropriate
        provider based on the configured provider type. The provider is responsible
        for the actual data operations.
        """
        self.config = TDConfig()
        self.provider: TDProvider = TDProviderFactory.get_provider(self.config.provider)

    async def load(self):
        """Load telco directory data from the configured provider.

        This method delegates the loading operation to the configured provider,
        logs the loading process, and prints the loaded data for debugging purposes.
        The method is idempotent and can be called multiple times safely.
        """
        if self.provider:
            self.logger.info(f"Loading telco directory with {self.provider.provider_type}")
            await self.provider.load()
            self.logger.info(f"Telco directory loaded successfully with {self.provider.provider_type}")
            print(self.provider.data)

    async def reload(self):
        """Reload telco directory data by clearing cache and loading fresh data.

        This method forces a refresh of the telco directory data by delegating
        to the provider's reload method, which clears internal caches and
        loads fresh data from the configured source.
        """
        if self.provider:
            await self.provider.reload()

    async def update(self, mcc: str, sn: str, data: SingleTelcoData):
        """Update telco data for a specific MCC and SN combination.

        Args:
            mcc: Mobile Country Code identifying the country/region.
            sn: Service Number or prefix to update.
            data: New telco data containing base_url, client_id, and client_secret.
        """
        if self.provider:
            await self.provider.update(mcc, sn, data)

    async def get_telco_data(self, mcc: str, sn: str) -> SingleTelcoData | None:
        """Retrieve telco data using longest prefix matching algorithm.

        This method combines the MCC and SN into a query string and uses the provider's
        longest prefix matching algorithm to find the most specific telco configuration
        that matches the given parameters.

        Args:
            mcc: Mobile Country Code identifying the country/region.
            sn: Service Number or phone number prefix to query.

        Returns:
            SingleTelcoData containing base_url, client_id, and client_secret if a match
            is found, None otherwise.
        """
        if self.provider:
            return await self.provider.get_telco_data(mcc, sn)
        return None


async def get_telco_directory() -> TelcoDirectory:
    """FastAPI dependency function to get a loaded TelcoDirectory singleton instance.

    This function serves as a FastAPI dependency that ensures the TelcoDirectory
    singleton is properly initialized and loaded before being injected into
    route handlers. It automatically handles the loading process and returns
    the ready-to-use instance.

    Returns:
        TelcoDirectory: Fully loaded singleton instance ready for telco operations.
    """
    telco_directory = TelcoDirectory()
    await telco_directory.load()
    return telco_directory


TelcoDirectoryDep = Annotated[TelcoDirectory, Depends(get_telco_directory)]
