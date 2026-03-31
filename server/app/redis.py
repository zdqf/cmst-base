"""Redis connection management with graceful degradation.

Provides a Redis client with connection pooling, health checks,
and automatic fallback when Redis is unavailable. When Redis is down,
dependents should allow requests through and log warnings.
"""

import logging
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import ConnectionError, RedisError

from app.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[ConnectionPool] = None
_redis: Optional[Redis] = None
_available: bool = False


async def init_redis() -> None:
    """Initialize the Redis connection pool.

    Called during application startup. If Redis is unreachable at startup,
    the pool is still created so reconnection can happen automatically.
    """
    global _pool, _redis, _available
    try:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
        _redis = Redis(connection_pool=_pool)
        # Verify connectivity
        await _redis.ping()
        _available = True
        logger.info("Redis connection established")
    except (ConnectionError, RedisError, OSError) as exc:
        _available = False
        logger.warning("Redis unavailable at startup, degraded mode active: %s", exc)


async def close_redis() -> None:
    """Close the Redis connection pool. Called during application shutdown."""
    global _pool, _redis, _available
    if _redis is not None:
        await _redis.aclose()
        _redis = None
    if _pool is not None:
        await _pool.aclose()
        _pool = None
    _available = False
    logger.info("Redis connection closed")


def get_redis() -> Optional[Redis]:
    """Return the Redis client instance, or None if not initialised."""
    return _redis


async def is_redis_available() -> bool:
    """Check whether Redis is currently reachable.

    Performs a lightweight PING and updates the internal availability flag.
    Callers can use this to decide whether to use Redis or fall back.
    """
    global _available
    if _redis is None:
        _available = False
        return False
    try:
        await _redis.ping()
        if not _available:
            logger.info("Redis connection recovered")
        _available = True
        return True
    except (ConnectionError, RedisError, OSError) as exc:
        if _available:
            logger.warning("Redis became unavailable: %s", exc)
        _available = False
        return False


def redis_available() -> bool:
    """Return the last-known Redis availability status (non-async)."""
    return _available
