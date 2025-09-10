from common_components.services.secret_manger.enums.providers import SMProvidersTypes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from common_components.services.secret_manger.provider.abs_provider import SMProvider


class SMProviderFactory:
    """Factory class for creating Secret Manager provider instances.

    This factory uses a registry pattern to manage and instantiate different types
    of secret manager providers. Providers must be registered before they can be
    created through the factory.

    The factory maintains a class-level dictionary that maps provider types to
    their corresponding provider classes, allowing for dynamic provider creation
    based on the requested provider type.
    """
    classes = {}

    @classmethod
    def register_class(cls, provider_type: SMProvidersTypes, provider_class: type['SMProvider']) -> None:
        """Register a provider class with the factory.

        Associates a provider type with its corresponding provider class implementation.
        This method must be called before attempting to create instances of the provider
        through the get_provider method.

        Args:
            provider_type: The type of secret manager provider to register.
            provider_class: The provider class that implements the SMProvider interface.
        """
        cls.classes[provider_type] = provider_class

    @classmethod
    def get_provider(cls, provider_type: SMProvidersTypes) -> 'SMProvider':
        """Create and return a provider instance of the specified type.

        Instantiates a new provider object based on the registered provider type.
        The provider class must have been previously registered using the
        register_class method.

        Args:
            provider_type: The type of secret manager provider to create.

        Returns:
            A new instance of the requested provider type.

        Raises:
            KeyError: If the provider_type has not been registered with the factory.
        """
        return cls.classes[provider_type]()
