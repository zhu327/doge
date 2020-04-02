from prometheus_client import Counter, Histogram  # type: ignore

from doge.common.doge import Request, Response
from doge.filter import BaseFilter

DOGE_CLIENT_STARTED_TOTAL_COUNTER = Counter(
    "doge_client_started_total",
    "Total number of RPCs started on the client",
    ["doge_service", "doge_method"],
)

DOGE_CLIENT_COMPLETED_COUNTER = Counter(
    "doge_client_completed",
    "Total number of RPCs completed on the client, "
    "regardless of success or failure.",
    ["doge_service", "doge_method", "code"],
)

DOGE_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM = Histogram(
    "doge_client_completed_latency_seconds",
    "Histogram of rpc response latency (in seconds) for completed rpcs.",
    ["doge_service", "doge_method"],
)


class MetricsClientFilter(BaseFilter):
    def execute(self, req: Request) -> Response:
        doge_service = req.service
        doge_method = req.method

        DOGE_CLIENT_STARTED_TOTAL_COUNTER.labels(
            doge_service=doge_service, doge_method=doge_method
        ).inc()

        with DOGE_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
            doge_service=doge_service, doge_method=doge_method
        ).time():
            res = self.next.execute(req)

        DOGE_CLIENT_COMPLETED_COUNTER.labels(
            doge_service=doge_service,
            doge_method=doge_method,
            code=0 if not res.exception else 1,
        ).inc()

        return res
