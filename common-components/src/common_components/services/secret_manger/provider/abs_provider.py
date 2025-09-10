from abc import ABC, abstractmethod
from common_components.services.secret_manger.configs.sm_provider_config import SMProviderConfig
from common_components.services.secret_manger.models.jwt_encryption import JWTEncryptionData
from common_components.services.secret_manger.enums.providers import SMProvidersTypes
from common_components.services.secret_manger.provider.provider_factory import SMProviderFactory
import inspect
import logging
from common_components.services.secret_manger.models.telco_auth import TelcoAuthData


class SMProvider(ABC):
    """Abstract base class for secret management providers.

    This class provides a framework for implementing different secret management providers
    with automatic factory registration, lazy loading capabilities, and JWT encryption key
    management. Concrete subclasses must implement the load() and _get_jwt_encryption_key()
    methods to define provider-specific behavior.

    The class automatically registers non-abstract subclasses with the SMProviderFactory
    during subclass creation, enabling dynamic provider instantiation based on provider type.
    """

    provider_type: SMProvidersTypes
    logger: logging.Logger = logging.getLogger(__name__)
    config_type: type[SMProviderConfig]

    def __init__(self) -> None:
        """Initialize the provider with default state.

        Sets up the provider with initial data as None and loaded status as False.
        The actual data loading is deferred until explicitly called through the load() method.
        """
        self.data = None
        self.loaded = False

    def __init_subclass__(cls, **kwargs) -> None:
        """Register non-abstract subclasses with the provider factory.

        This method is automatically called when a class inherits from SMProvider.
        It registers concrete implementations (non-abstract classes) with the
        SMProviderFactory using the class's provider_type as the key.

        Args:
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super().__init_subclass__(**kwargs)
        SMProviderFactory.register_class(cls.provider_type, cls) if not inspect.isabstract(cls) else None

    @abstractmethod
    async def load(self) -> None:
        """Load provider-specific data asynchronously.

        This method must be implemented by concrete subclasses to define how the provider
        loads its configuration and data. The implementation should set the loaded status
        and populate the data attribute as needed.
        """
        ...

    @abstractmethod
    def get_jwt_encryption_key(self) -> JWTEncryptionData:
        """Get JWT encryption key data with automatic loading verification.

        This method ensures the provider is loaded before attempting to retrieve
        the JWT encryption key. The @loaded_first decorator validates that the
        provider has been loaded and has data available before proceeding.

        Returns:
            JWTEncryptionData: The JWT encryption key data from the provider.
        """
        ...

    @abstractmethod
    def get_telco_auth(self) -> TelcoAuthData:
        """Get telco authentication data.

        Returns:
            TelcoAuthData: Telco authentication data.
        """
        ...
