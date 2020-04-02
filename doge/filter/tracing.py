# coding: utf-8

import opentracing  # type: ignore
from opentracing.ext import tags  # type: ignore
from opentracing.propagation import Format  # type: ignore

from doge.common.doge import Request, Response
from doge.filter import BaseFilter

tracer = opentracing.global_tracer()


class TracingClientFilter(BaseFilter):
    def execute(self, req: Request) -> Response:
        with tracer.start_active_span(req.method) as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
            scope.span.set_tag("doge_service", req.service)
            scope.span.set_tag("doge_method", req.method)
            tracer.inject(scope.span, Format.TEXT_MAP, req.meta)

            res = self.next.execute(req)
            if res.exception:
                scope.span.set_tag("error", True)
                scope.span.log_event(
                    {"event": "error", "exception": res.exception}
                )
            return res


class TracingServerFilter(BaseFilter):
    def execute(self, req: Request) -> Response:
        span_ctx = tracer.extract(Format.TEXT_MAP, req.meta)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}

        with tracer.start_active_span(
            req.method, child_of=span_ctx, tags=span_tags
        ) as scope:
            scope.span.set_tag("doge_service", req.service)
            scope.span.set_tag("doge_method", req.method)

            res = self.next.execute(req)
            if res.exception:
                scope.span.set_tag("error", True)
                scope.span.log_event(
                    {"event": "error", "exception": res.exception}
                )
            return res
