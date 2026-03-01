from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_COUNTER = Counter(
    "app_requests_total",
    "Total number of requests by endpoint and method.",
    ["endpoint", "method", "status"],
)

LATENCY_HISTOGRAM = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds by endpoint and method.",
    ["endpoint", "method"],
    buckets=(0.1, 0.3, 0.5, 0.75, 1.0, 2.0, 5.0),
)

ERROR_COUNTER = Counter(
    "app_errors_total",
    "Number of internal server errors.",
)

WARNING_COUNTER = Counter(
    "app_warnings_total",
    "Number of warning-level events.",
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that exports custom request counters and latency histograms."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start = time.perf_counter()
        path = request.url.path
        method = request.method
        try:
            response = await call_next(request)
            route = request.scope.get("route")
            endpoint = getattr(route, "path", path)
            status = str(response.status_code)
            REQUEST_COUNTER.labels(endpoint=endpoint, method=method, status=status).inc()
            LATENCY_HISTOGRAM.labels(endpoint=endpoint, method=method).observe(
                time.perf_counter() - start
            )
            if response.status_code >= 500:
                ERROR_COUNTER.inc()
            return response
        except Exception:
            ERROR_COUNTER.inc()
            raise


def increment_warning() -> None:
    """Increment warning metric for observable bottlenecks/events."""
    WARNING_COUNTER.inc()
