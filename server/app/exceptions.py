"""Unified application exception hierarchy.

Requirements:
- 16.1: Define AppException base class and NotFoundError(404), UnauthorizedError(401),
         ForbiddenError(403), RateLimitError(429) subclasses
- 16.2: Global handler catches AppException and returns standard JSON {code, message}
- 16.3: Unexpected exceptions return HTTP 500 with generic message, no internal details
"""


class AppException(Exception):
    """Application base exception.

    All service-layer errors should raise an AppException subclass
    so the global handler can return a consistent JSON response.
    """

    def __init__(self, code: int = 400, message: str = "请求错误"):
        self.code = code
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found (HTTP 404)."""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class UnauthorizedError(AppException):
    """Authentication required (HTTP 401)."""

    def __init__(self, message: str = "未授权"):
        super().__init__(code=401, message=message)


class ForbiddenError(AppException):
    """Permission denied (HTTP 403)."""

    def __init__(self, message: str = "无权限"):
        super().__init__(code=403, message=message)


class RateLimitError(AppException):
    """Too many requests (HTTP 429)."""

    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(code=429, message=message)
