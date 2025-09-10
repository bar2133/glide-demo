from abc import abstractmethod
from fastapi import APIRouter
from enum import Enum
from ...utils.metaclasses.singlethon import Singleton
from .registry import RouteRegistry
import inspect
import logging


class AbstractRouter(metaclass=Singleton):
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, prefix: str = "", tags: list[str | Enum] | None = None):
        self.prefix = prefix
        self.tags = tags
        self.router = APIRouter(prefix=prefix, tags=self.tags)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls):
            RouteRegistry.register_route(cls)

    @abstractmethod
    def register_routes(self):
        pass
