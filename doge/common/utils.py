# coding: utf-8

import time
from importlib import import_module
from typing import Any, Tuple

from gsocketpool.pool import Pool  # type: ignore
from jaeger_client import Config  # type: ignore
from jaeger_client.tracer import Tracer  # type: ignore
from mprpc.client import RPCPoolClient  # type: ignore


def import_string(dotted_path: str,) -> Any:
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            dotted_path,
            class_name,
        )
        raise ImportError(msg)


def time_ns() -> float:
    s, n = ("%.20f" % time.time()).split(".")
    return int(s) * 1e9 + int(n[:9])


def str_to_host(s: str) -> Tuple[str, int]:
    h, p = s.split(":")
    return (str(h), int(p))


class ConnPool(Pool):
    def _create_connection(self) -> RPCPoolClient:
        conn = self._factory(**self._options)
        # conn.open()

        return conn


def init_tracer(service: str) -> Tracer:
    config = Config(
        config={"sampler": {"type": "const", "param": 1}, "logging": True},
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()
