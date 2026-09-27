"""Prometheus metrics for AI provider evaluation outcomes."""

from prometheus_client import Counter, Histogram

EVALUATIONS = Counter(
    "resumerank_ai_evaluations_total",
    "AI evaluation attempts by provider and outcome.",
    ("provider", "outcome"),
)
EVALUATION_DURATION = Histogram(
    "resumerank_ai_evaluation_duration_seconds",
    "End-to-end AI evaluation duration in seconds.",
    ("provider",),
)
