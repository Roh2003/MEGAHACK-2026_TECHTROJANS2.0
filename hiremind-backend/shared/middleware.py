"""
Shared middlewares — register on any FastAPI app instance.

Available:
    LoggingMiddleware  — logs method, path, status code and response time

Usage in main.py:
    from shared.middleware import LoggingMiddleware
    app.add_middleware(LoggingMiddleware)
"""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming request with method, path, status code, and duration.

    Example output:
        2026-03-12 10:00:01 | INFO | POST /auth/register → 201 (45ms)
        2026-03-12 10:00:02 | INFO | GET  /jobs          → 200 (12ms)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s → %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
