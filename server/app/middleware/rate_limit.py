"""API rate limiting middleware using Redis sorted sets (sliding window).

Requirements:
- 18.1: Sliding window rate limiting backed by Redis
- 18.2: Return HTTP 429 when request rate exceeds the configured threshold
- 18.3: Degrade gracefully (allow all requests) when Redis is unavailable
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.redis import get_redis, is_redis_available

logger = logging.getLogger(__name__)

# Defaults
DEFAULT_RATE_LIMIT = 60  # requests per window
DEFAULT_WINDOW = 60  # seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP.

    Uses a Redis sorted set per IP. Each request adds a member scored by
    the current timestamp. Members older than the window are pruned, and
    the remaining count is compared against the limit.

    When Redis is unavailable the middleware degrades to allow-all and
    logs a warning.
    """

    def __init__(self, app, rate_limit: int = DEFAULT_RATE_LIMIT, window: int = DEFAULT_WINDOW):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        exceeded = await self._check_rate_limit(key, self.rate_limit, self.window)
        if exceeded:
            return JSONResponse(
                status_code=429,
                content={"code": 429, "message": "请求过于频繁"},
            )

        return await call_next(request)

    async def _check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Return True if the rate limit has been exceeded.

        Uses a Redis sorted set as a sliding window. Returns False
        (allow) when Redis is unavailable so the system degrades
        gracefully.
        """
        if not await is_redis_available():
            logger.warning("Redis unavailable — rate limiting disabled, allowing request")
            return False

        redis = get_redis()
        if redis is None:
            logger.warning("Redis client is None — rate limiting disabled, allowing request")
            return False

        now = time.time()
        window_start = now - window
        member = f"{now}:{uuid.uuid4().hex[:8]}"

        try:
            async with redis.pipeline() as pipe:
                # Remove entries outside the current window
                await pipe.zremrangebyscore(key, 0, window_start)
                # Add the current request
                await pipe.zadd(key, {member: now})
                # Count requests in the window
                await pipe.zcard(key)
                # Set expiry so keys don't linger forever
                await pipe.expire(key, window)
                results = await pipe.execute()

            current_count = results[2]
            return current_count > limit
        except Exception:
            logger.warning("Redis error during rate limit check — allowing request", exc_info=True)
            return False
