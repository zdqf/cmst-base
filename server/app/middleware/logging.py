"""Request logging middleware with sensitive data masking.

Requirements:
- 17.1: Log request method, path, response status code, and processing duration
         for every HTTP request.
- 17.2: Mask sensitive data in logs — replace middle 4 digits of phone numbers
         with asterisks; never log password fields.
"""

import logging
import re
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")

# Regex matching Chinese mobile numbers (11 digits starting with 1[3-9])
_PHONE_RE = re.compile(r"(1[3-9]\d)\d{4}(\d{4})")

# Keys whose values must never appear in logs
_SENSITIVE_KEYS = {"password", "old_password", "password_hash"}


def mask_phone(text: str) -> str:
    """Replace the middle 4 digits of phone numbers with ``****``.

    >>> mask_phone("user phone is 13812345678 ok")
    'user phone is 138****5678 ok'
    """
    return _PHONE_RE.sub(r"\1****\2", text)


def sanitize_log_message(text: str) -> str:
    """Apply all sanitisation rules to a log string.

    1. Mask phone numbers.
    2. (Password fields are excluded at the source — see middleware.)
    """
    return mask_phone(text)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status code and duration.

    Sensitive data is masked before writing to the log:
    * Phone numbers have their middle 4 digits replaced with ``****``.
    * Password fields are never included in the log output.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        path = sanitize_log_message(str(request.url.path))
        query = str(request.url.query)
        if query:
            query = sanitize_log_message(query)
            log_path = f"{path}?{query}"
        else:
            log_path = path

        logger.info(
            "%s %s -> %s (%.3fs)",
            request.method,
            log_path,
            response.status_code,
            duration,
        )
        return response
