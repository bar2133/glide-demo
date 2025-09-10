from common_components.services.telco_directory.enums.providers import TDProvidersTypes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from common_components.services.telco_directory.providers.abs_provider import TDProvider


class TDProviderFactory:
    """Factory class for creating telco directory provider instances.

    This factory implements the Factory pattern to create instances of telco directory
    providers based on their provider type. It maintains a registry of provider classes
    and provides methods to register new provider types and instantiate providers.

    The factory uses a class-level dictionary to store mappings between provider types
    (TDProvidersTypes enum values) and their corresponding provider classes that
    implement the TDProvider abstract base class.
    """
    classes = {}

    @classmethod
    def register_class(cls, provider_type: TDProvidersTypes, provider_class: type['TDProvider']):
        """Register a provider class with the factory.

        This method associates a provider type enum value with its corresponding
        provider class implementation. Provider classes are typically registered
        automatically through the TDProvider.__init_subclass__ method when they
        are defined.

        Args:
            provider_type: The enum value identifying the provider type.
            provider_class: The provider class that implements TDProvider interface.
        """
        cls.classes[provider_type] = provider_class

    @classmethod
    def get_provider(cls, provider_type: TDProvidersTypes) -> 'TDProvider':
        """Create and return a new instance of the specified provider type.

        This method retrieves the provider class associated with the given provider
        type from the internal registry and instantiates it. The returned instance
        is ready to use for telco directory operations.

        Args:
            provider_type: The enum value identifying the desired provider type.

        Returns:
            A new instance of the provider class corresponding to the provider type.

        Raises:
            KeyError: If the provider_type is not registered in the factory.
        """
        return cls.classes[provider_type]()
