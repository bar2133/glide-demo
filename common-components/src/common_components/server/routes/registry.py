from ...utils.metaclasses.singlethon import Singleton
from typing import TYPE_CHECKING
from fastapi import FastAPI, APIRouter
import logging
from ...configurations.server_config import ServerConfig
if TYPE_CHECKING:
    from .abstract_router import AbstractRouter


class RouteRegistry(metaclass=Singleton):
    routes: list['AbstractRouter'] = []
    logger = logging.getLogger(__name__)
    server_config = ServerConfig()

    @classmethod
    def register_route(cls, route: type['AbstractRouter']):
        try:
            route_instance = route()
            route_instance.register_routes()
            cls.routes.append(route_instance)
        except Exception as e:
            cls.logger.error(f"Error registering route {route.__name__}: {e}")

    @classmethod
    def include_routes(cls, app: FastAPI):
        root_prefix = f"/api/{cls.server_config.version}" if cls.server_config.version else "/api"
        root_router = APIRouter(prefix=root_prefix)
        for route in cls.routes:
            try:
                root_router.include_router(route.router)
            except Exception as e:
                cls.logger.error(f"Error registering route {route.__name__}: {e}")
        app.include_router(root_router)
