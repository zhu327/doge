# coding: utf-8

import logging
from jaeger_client import Config
from opentracing.ext import tags
from opentracing.propagation import Format

from doge.filter import BaseFilter


def init_tracer(service):
    logging.getLogger("tracing").handlers = []
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    config = Config(
        config={"sampler": {"type": "const", "param": 1}, "logging": True},
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


tracer = None


class TracingClientFilter(BaseFilter):
    def __init__(self, client, _next):
        super(TracingClientFilter, self).__init__(client, _next)
        global tracer
        if not tracer:
            tracer = init_tracer(client.service)

    def execute(self, req):
        with tracer.start_active_span(req.method) as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
            tracer.inject(scope.span, Format.TEXT_MAP, req.meta)
            res = self.next.execute(req)
        return res


class TracingServerFilter(BaseFilter):
    def __init__(self, server, _next):
        super(TracingServerFilter, self).__init__(server, _next)
        global tracer
        if not tracer:
            tracer = init_tracer(server.name)

    def execute(self, req):
        span_ctx = tracer.extract(Format.TEXT_MAP, req.meta)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}

        with tracer.start_active_span(
            req.method,
            child_of=span_ctx,
            tags=span_tags
        ):
            res = self.next.execute(req)
            return res
