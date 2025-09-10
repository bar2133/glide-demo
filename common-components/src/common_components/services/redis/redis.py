from common_components.utils.metaclasses.singlethon import Singleton
from common_components.services.redis.configs.redis_config import RedisConfig
from redis.asyncio import Redis
import logging
from typing import Annotated
from fastapi import Depends
from common_components.models.telecom_dto import TelecomIdentifierDTO
from common_components.services.redis.enums.key_types import CacheKeyType


class RedisService(metaclass=Singleton):
    """Redis service for managing cache operations using async Redis client.

    This service implements the Singleton pattern to ensure only one Redis connection
    instance exists throughout the application lifecycle. It provides methods for
    setting and getting cached values with expiration times, and includes connection
    management with error handling.
    """
    logger: logging.Logger = logging.getLogger(__name__)
    INIT_CONNECTION_FAILED: bool = False

    def __init__(self):
        """Initialize RedisService with configuration and null Redis client.

        Sets up the Redis configuration from RedisConfig and initializes
        the Redis client as None, requiring explicit connection initialization.
        """
        self.config = RedisConfig()
        self.redis: Redis | None = None

    def init_connection(self):
        """Initialize Redis connection using configuration parameters.

        Creates an async Redis client connection using host, port, password,
        and database settings from the configuration. Sets INIT_CONNECTION_FAILED
        flag to True and logs error if connection initialization fails.

        Raises:
            Exception: If Redis connection initialization fails for any reason.
        """
        try:
            self.redis = Redis(host=self.config.host, port=self.config.port,
                               password=self.config.password, db=self.config.db)
        except Exception as e:
            self.INIT_CONNECTION_FAILED = True
            self.logger.error(f"Error initializing Redis connection: {e}")
            raise e

    async def set_value(self, key: str, value: str, exp_sec: int):
        """Set a key-value pair in Redis with expiration time.

        Stores the provided value under the specified key with an expiration
        time in seconds. If Redis connection is not initialized, logs an error
        and raises an exception.

        Args:
            key: The cache key to store the value under.
            value: The string value to store in the cache.
            exp_sec: Expiration time in seconds for the cached value.

        Raises:
            Exception: If Redis connection is not initialized.
        """
        if self.redis:
            await self.redis.setex(name=key, time=exp_sec, value=value)
        else:
            self.logger.error("Redis connection not initialized")
            raise Exception("Redis connection not initialized")

    async def get_value(self, key: str) -> str | None:
        """Retrieve a value from Redis by key.

        Fetches the value associated with the specified key from Redis cache.
        Returns None if the key doesn't exist or has expired. If Redis connection
        is not initialized, logs an error and raises an exception.

        Args:
            key: The cache key to retrieve the value for.

        Returns:
            The cached string value if found, None if key doesn't exist or expired.

        Raises:
            Exception: If Redis connection is not initialized.
        """
        if self.redis:
            return await self.redis.get(name=key)
        else:
            self.logger.error("Redis connection not initialized")
            raise Exception("Redis connection not initialized")

    @staticmethod
    def get_key(key_type: CacheKeyType, telco_data: TelecomIdentifierDTO) -> str:
        """Generate a standardized cache key from key type and telecom data.

        Creates a formatted cache key by combining the cache key type value
        with the mobile country code (mcc) and serial number (sn) from the
        telecom identifier data.

        Args:
            key_type: The type of cache key from CacheKeyType enum.
            telco_data: Telecom identifier containing mcc and sn values.

        Returns:
            A formatted string key in the format: "{key_type}_{mcc}_{sn}".
        """
        return f"{key_type.value}_{telco_data.mcc}_{telco_data.sn}"

    def is_initialized(self) -> bool:
        """Check if Redis service is properly initialized and ready for use.

        Verifies that the Redis client is not None and that no connection
        initialization failure has occurred.

        Returns:
            True if Redis is initialized and connection didn't fail, False otherwise.
        """
        return self.redis is not None and not self.INIT_CONNECTION_FAILED


def get_redis_service() -> RedisService | None:
    """Factory function to get a Redis service instance with connection management.

    Creates or retrieves a Redis service instance using the Singleton pattern.
    Handles connection initialization and returns None if connection failed.
    If the service is not initialized, attempts to initialize the connection.

    Returns:
        RedisService instance if connection is successful, None if connection failed.
    """
    instance = RedisService()
    if instance.INIT_CONNECTION_FAILED:
        return None
    if not instance.is_initialized():
        instance.init_connection()
    return instance


RedisDep = Annotated[RedisService | None, Depends(get_redis_service)]
