from abc import ABC, abstractmethod
from common_components.services.telco_directory.models.td_data import SingleTelcoData, TDData
from common_components.services.telco_directory.configs.td_provider import TDProviderConfig
from functools import lru_cache
from common_components.services.telco_directory.enums.providers import TDProvidersTypes
from common_components.services.telco_directory.providers.provider_factory import TDProviderFactory
import inspect
import logging
from common_components.utils.loaded_wrapper import loaded_first


class TDProvider(ABC):
    """Abstract base class for telco directory data providers.

    This class serves as the foundation for implementing different types of telco directory
    data providers. It provides a standardized interface for loading, reloading, and querying
    telco data using longest prefix matching algorithms. The class automatically registers
    concrete implementations with the provider factory and includes caching mechanisms
    for performance optimization.

    The provider uses a longest prefix matching strategy to find telco data based on
    MCC (Mobile Country Code) and SN (Service Number) combinations. It maintains
    internal state for loaded data and provides decorators for ensuring data is
    loaded before operations.
    """
    provider_type: TDProvidersTypes
    logger: logging.Logger = logging.getLogger(__name__)
    config_type: type[TDProviderConfig]

    def __init__(self):
        """Initialize the telco directory provider.

        Creates a new instance with configuration based on the config_type,
        initializes the loaded state to False, and sets data to None.
        """
        self.config: TDProviderConfig = self.config_type()
        self.loaded = False
        self.data: TDData | None = None

    def __init_subclass__(cls, **kwargs):
        """Register concrete subclasses with the provider factory.

        This method is automatically called when a class inherits from TDProvider.
        It registers non-abstract subclasses with the TDProviderFactory using their
        provider_type as the key.

        Args:
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super().__init_subclass__(**kwargs)
        TDProviderFactory.register_class(cls.provider_type, cls) if not inspect.isabstract(cls) else None

    @abstractmethod
    async def load(self):
        """Load telco directory data from the configured source.

        This abstract method must be implemented by concrete provider classes
        to load telco data from their specific data source. The implementation
        should set self.data with the loaded TDData and self.loaded to True
        upon successful loading.
        """
        ...

    async def reload(self):
        """Reload telco directory data by clearing current state and loading fresh data.

        This method resets the provider state by setting loaded to False, clearing
        the data, and clearing the LRU cache for sorted prefixes. It then calls
        the load method to fetch fresh data from the configured source.
        """
        self.loaded = False
        self.data = None
        # Clear the cache when reloading data
        self._get_sorted_prefixes.cache_clear()
        await self.load()

    @loaded_first(need_data=False)
    async def update(self, mcc: str, sn: str, data: SingleTelcoData):
        """Update telco data for a specific MCC and SN combination.

        This method provides a placeholder for updating telco data entries.
        The loaded_first decorator ensures the provider is loaded before
        attempting the update operation.

        Args:
            mcc: Mobile Country Code to update.
            sn: Service Number to update.
            data: New telco data to associate with the MCC+SN combination.
        """
        ...

    @lru_cache(1)
    def _get_sorted_prefixes(self, prefixes_tuple: tuple[str, ...]) -> tuple[str, ...]:
        """Get sorted prefixes using LRU cache for performance.

        Args:
            prefixes_tuple: Tuple of prefix keys to sort.

        Returns:
            Tuple of prefixes sorted by length in descending order (longest first).
        """
        return tuple(sorted(prefixes_tuple, key=len, reverse=True))

    def _find_longest_prefix_match(self, query: str) -> str | None:
        """Find the prefix with the biggest intersection from the start of the query string.

        This method finds the prefix that has the maximum number of matching characters
        from the beginning of the query string, not requiring the full prefix to match.
        Uses optimized string operations and early termination for better performance.

        Args:
            query: The query string to find prefix match for (e.g., MCC+SN combination).

        Returns:
            The prefix key with the biggest intersection from start, or None if no intersection found.
        """
        if not self.data or not self.data.prefixes or not query:
            return None

        for prefix in self._get_sorted_prefixes(tuple(self.data.prefixes.keys())):
            if query.startswith(prefix):
                self.logger.info(f"Best prefix for {query}: {prefix}")
                return prefix
        self.logger.info(f"No prefix found for {query}")
        return None

    @loaded_first(need_data=True)
    async def get_telco_data(self, mcc: str, sn: str) -> SingleTelcoData | None:
        """Get telco data using longest prefix matching.

        Args:
            mcc: Mobile Country Code.
            sn: Service Number.

        Returns:
            SingleTelcoData if a prefix match is found, None otherwise.
        """
        query = f"{mcc}{sn}"

        # Then try longest prefix match
        longest_prefix = self._find_longest_prefix_match(query)
        if longest_prefix and self.data:
            return self.data.prefixes[longest_prefix]

        return None
