"""Low-cardinality Prometheus metrics for the backend."""

from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from starlette.responses import Response


HTTP_REQUESTS = Counter(
    "resumerank_http_requests_total",
    "HTTP requests handled by the API.",
    ("method", "path", "status"),
)
HTTP_REQUEST_DURATION = Histogram(
    "resumerank_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "path"),
)
SCREENING_STARTS = Counter(
    "resumerank_screening_starts_total",
    "Screenings successfully scheduled for processing.",
)


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
