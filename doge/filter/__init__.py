from gevent.monkey import patch_thread

patch_thread()


class BaseFilter(object):
    def __init__(self, holder, _next):
        self.next = _next

    def execute(self, req):
        self.next.execute(req)


class FilterChain(object):
    def __init__(self, filters):
        self.filters = filters

    def then(self, holder):
        f = holder
        for filter_cls in reversed(self.filters):
            f = filter_cls(holder, f)
        return f
