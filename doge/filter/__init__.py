from gevent.monkey import patch_thread  # type: ignore

from doge.common.utils import import_string

patch_thread()


class BaseFilter(object):
    def __init__(self, context, _next):
        self.next = _next

    def execute(self, req):
        self.next.execute(req)


class FilterChain(object):
    def __init__(self, context):
        self.context = context

    def then(self, executer):
        filters = self.context.url.get_param("filters", [])
        for cls in reversed([import_string(f) for f in filters]):
            executer = cls(self.context, executer)
        return executer
