"""Prometheus metrics integration for FastAPI."""
from __future__ import annotations

from fastapi import APIRouter
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "pulse_http_requests_total",
    "Total HTTP requests processed by the gateway",
    labelnames=("method", "path", "status"),
)
REQUEST_LATENCY = Histogram(
    "pulse_http_request_latency_seconds",
    "HTTP request latency",
    labelnames=("method", "path"),
)

metrics_router = APIRouter()


@metrics_router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")
