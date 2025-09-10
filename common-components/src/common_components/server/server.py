import uvicorn
from fastapi import FastAPI
from .routes.registry import RouteRegistry
from ..configurations.server_config import ServerConfig
import logging


class APIServer:
    """FastAPI server wrapper with configuration management and route registration.

    Provides a configurable FastAPI server with automatic route registration
    through RouteRegistry and optional hot reload support for development.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, server_config: ServerConfig | None = None) -> None:
        """Initialize the API server with FastAPI application and route registration.

        Creates a FastAPI application instance, applies the provided server configuration
        or uses default configuration, registers routes through RouteRegistry, and
        performs post-initialization setup.

        Args:
            server_config: Optional server configuration. If None, uses default ServerConfig.
        """
        self.server_config = server_config or ServerConfig()
        self.app = FastAPI()
        RouteRegistry.include_routes(self.app)
        self.__post_init__()

    def __post_init__(self) -> None:
        """Perform post-initialization setup tasks.

        Called automatically after the main initialization to perform additional
        setup tasks such as printing registered routes for debugging purposes.
        """
        self._print_registered_routes()

    def run(self, start_path: str = "") -> None:
        """Start the FastAPI server with uvicorn.

        Runs the server using uvicorn with configuration from server_config.
        Supports both hot reload mode for development and production mode.
        In hot reload mode, uses the provided start_path as import string.
        In production mode, uses the FastAPI app instance directly.

        Args:
            start_path: Import path string for hot reload mode (e.g., "app:app").
                       Only used when hot_reload is enabled in server configuration.
        """
        if self.server_config.hot_reload:
            # Use import string for hot reload
            uvicorn.run(
                start_path,
                host=self.server_config.host,
                port=self.server_config.port,
                reload=True,
            )
        else:
            # Use app instance for production
            uvicorn.run(
                self.app,
                host=self.server_config.host,
                port=self.server_config.port,
                reload=False
            )

    def _print_registered_routes(self) -> None:
        """Log all registered routes in a formatted table for debugging.

        Iterates through the FastAPI router's routes and logs each route's
        HTTP methods, path, and name in a formatted table structure.
        Routes without standard attributes are logged as-is.
        """
        self.logger.info("\nRegistered Routes:")
        self.logger.info("-" * 50)
        for route in self.app.router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(sorted(route.methods)) if route.methods else 'N/A'  # type: ignore
                route_name = getattr(route, 'name', 'unnamed')
                self.logger.info(f"[{methods:<10}]    {route.path:<25}  ({route_name})")  # type: ignore
            else:
                self.logger.info(f"    {route}")
        self.logger.info("-" * 50)
