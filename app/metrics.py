"""
Prometheus Metrics for NLP App
"""
from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter(
    "nlp_request_count_total",
    "Total number of requests to NLP API",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "nlp_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

GENERATION_TIME = Histogram(
    "nlp_generation_time_seconds",
    "Time taken to generate text",
)

MODEL_CALLS = Counter(
    "nlp_model_calls_total",
    "Total number of model calls",
    ["status"]
)
