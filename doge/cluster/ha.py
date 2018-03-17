# coding: utf-8

from doge.common.exceptions import RemoteError
from doge.common.doge import Response

defaultRetries = 0


class FailOverHA(object):
    def __init__(self, url):
        self.url = url
        self.name = "failover"

    def call(self, request, lb):
        retries = self.url.get_method_positive_int_value(
            request.method, "retries", defaultRetries)

        i = 0
        while i <= retries:
            i += 1
            ep = lb.select(request)
            if not ep:
                return Response(exception=RemoteError('no available endpoint'))
            res = ep.call(request)
            if not res.exception:
                return res
        return res
