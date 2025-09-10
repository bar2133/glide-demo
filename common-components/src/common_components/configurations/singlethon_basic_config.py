from pydantic_settings import BaseSettings
from common_components.utils.metaclasses.singlethon import Singleton
from pydantic._internal._model_construction import ModelMetaclass
from typing import ClassVar
import logging
from typing import Any


class SingletonModelMetaclass(ModelMetaclass, Singleton):
    """Metaclass that combines Singleton and ModelMetaclass functionality.

    This metaclass ensures that the class is both a singleton and a Pydantic model.
    """
    pass


class SingletonBasicConfig(BaseSettings, metaclass=SingletonModelMetaclass):
    """Base configuration class that implements singleton pattern.

    This class combines Pydantic's BaseSettings with singleton functionality.
    """
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)

    def model_post_init(self, __context: Any) -> None:
        """Print all configuration attributes after initialization.

        Args:
            __context: The context of the initialization.
        """
        self.logger.info("*" * 10)
        self.logger.info(f"{self.__class__.__name__} initialized with the following settings:")
        for key, value in self.model_dump().items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("*" * 10)
