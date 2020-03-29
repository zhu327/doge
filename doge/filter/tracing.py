# coding: utf-8

import opentracing
from opentracing.ext import tags
from opentracing.propagation import Format

from doge.filter import BaseFilter


tracer = opentracing.global_tracer()


class TracingClientFilter(BaseFilter):
    def __init__(self, context, _next):
        super(TracingClientFilter, self).__init__(context, _next)

    def execute(self, req):
        with tracer.start_active_span(req.method) as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
            tracer.inject(scope.span, Format.TEXT_MAP, req.meta)
            res = self.next.execute(req)
            if res.exception:
                scope.span.set_tag("error", True)
                scope.span.log_event(
                    {"event": "error", "exception": res.exception}
                )
            return res


class TracingServerFilter(BaseFilter):
    def __init__(self, context, _next):
        super(TracingServerFilter, self).__init__(context, _next)

    def execute(self, req):
        span_ctx = tracer.extract(Format.TEXT_MAP, req.meta)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}

        with tracer.start_active_span(
            req.method, child_of=span_ctx, tags=span_tags
        ):
            res = self.next.execute(req)
            return res
