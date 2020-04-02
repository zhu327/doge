from typing import Any

from gevent.monkey import patch_thread  # type: ignore

from doge.common.utils import import_string
from doge.common.doge import Executer, Request, Response

patch_thread()


class BaseFilter(Executer):
    def __init__(self, context: Any, _next: Executer):
        self.next = _next

    def execute(self, req: Request) -> Response:
        return self.next.execute(req)


class FilterChain(object):
    def __init__(self, context: Any):
        self.context = context

    def then(self, executer: Executer) -> Executer:
        filters = self.context.url.get_param("filters", [])
        for cls in reversed([import_string(f) for f in filters]):
            executer = cls(self.context, executer)
        return executer
