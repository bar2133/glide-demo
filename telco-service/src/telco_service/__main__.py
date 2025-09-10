from fastapi import FastAPI
from common_components.server.server import APIServer
from common_components.utils.logging_config import configure_basic_logger, setup_application_logging


configure_basic_logger()
setup_application_logging()


def hot_reload() -> FastAPI:
    """Hot reload the server."""
    server = APIServer()
    return server.app


def main() -> None:
    """Main entry point for the telco service."""
    server = APIServer()
    server.run("telco_service.__main__:hot_reload")


if __name__ == "__main__":
    main()
