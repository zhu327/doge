from prometheus_client import Counter, Histogram  # type: ignore

from doge.common.doge import Request, Response
from doge.filter import BaseFilter

DOGE_SERVER_STARTED_TOTAL_COUNTER = Counter(
    "doge_server_started_total",
    "Total number of RPCs started on the server.",
    ["doge_service", "doge_method"],
)

DOGE_SERVER_HANDLED_TOTAL_COUNTER = Counter(
    "doge_server_handled_total",
    (
        "Total number of RPCs completed on the server, "
        "regardless of success or failure."
    ),
    ["doge_service", "doge_method", "code"],
)

DOGE_SERVER_HANDLED_LATENCY_SECONDS = Histogram(
    "doge_server_handled_latency_seconds",
    "Histogram of response latency (seconds) of gRPC that had been "
    "application-level handled by the server",
    ["doge_service", "doge_method"],
)


class MetricsServerFilter(BaseFilter):
    def execute(self, req: Request) -> Response:
        doge_service = req.service
        doge_method = req.method

        DOGE_SERVER_STARTED_TOTAL_COUNTER.labels(
            doge_service=doge_service, doge_method=doge_method
        ).inc()

        with DOGE_SERVER_HANDLED_LATENCY_SECONDS.labels(
            doge_service=doge_service, doge_method=doge_method
        ).time():
            res = self.next.execute(req)

        DOGE_SERVER_HANDLED_TOTAL_COUNTER.labels(
            doge_service=doge_service,
            doge_method=doge_method,
            code=0 if not res.exception else 1,
        ).inc()

        return res
