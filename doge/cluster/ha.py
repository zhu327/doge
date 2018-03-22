# coding: utf-8

import logging

import gevent

from pyformance import MetricsRegistry

from doge.common.exceptions import RemoteError
from doge.common.doge import Response
from doge.common.utils import time_ns

defaultRetries = 0

counterRoundCount = 100  # 默认每100次请求为一个计数周期
counterScaleThreshold = 20 * 1e9  # 如果20s都没有经历一个循环周期则重置，防止过度饥饿
defaultBackupRequestDelayRatio = 90  # 默认的请求延迟的水位线，P90
defaultBackupRequestMaxRetryRatio = 15  # 最大重试比例
defaultRequestTimeout = 1000

logger = logging.getLogger('doge.cluster.ha')


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


class BackupRequestHA(object):
    def __init__(self, url):
        self.url = url
        self.name = "backupRequestHA"

        self.curRoundTotalCount = 0
        self.curRoundRetryCount = 0

        self.init()

    def init(self):
        self.registry = MetricsRegistry()
        self.lastResetTime = time_ns()

    def call(self, request, lb):
        ep_list = lb.select_list(request)
        if not ep_list:
            return Response(exception=RemoteError('no available endpoint'))
        retries = self.url.get_method_int_value(request.method, 'retries', 0)
        if retries == 0:
            return self.do_call(request, ep_list[0])

        backupRequestDelayRatio = self.url.get_method_positive_int_value(
            request.method, "backupRequestDelayRatio",
            defaultBackupRequestDelayRatio)
        backupRequestMaxRetryRatio = self.url.get_method_positive_int_value(
            request.method, "backupRequestMaxRetryRatio",
            defaultBackupRequestMaxRetryRatio)
        requestTimeout = self.url.get_method_positive_int_value(
            request.method, "requestTimeout", defaultRequestTimeout)

        histogram = self.registry.histogram(request.method)
        delay = int(histogram.get_snapshot().get_percentile(
            backupRequestDelayRatio / 100.0))
        if delay < 10:
            delay = 10

        logger.debug('service: %s method: %s ha delay: %s' %
                     (request.service, request.method, str(delay)))

        with gevent.Timeout(requestTimeout / 1000.0, False):
            i = 0
            while i <= retries and i < len(ep_list):
                ep = ep_list[i]
                if i == 0:
                    self.update_call_record(counterRoundCount)
                if i > 0 and not self.try_acquirePermit(
                        backupRequestMaxRetryRatio):
                    break

                def func():
                    start = time_ns()
                    res = self.do_call(request, ep)
                    if not res.exception:
                        histogram.add(float(time_ns() - start) / 1e6)
                        return res

                g = gevent.spawn(func)
                try:
                    res = g.get(timeout=(delay / 1000.0))
                    if res: return res
                except gevent.timeout.Timeout:
                    pass

                i += 1

        return Response(exception=RemoteError('request timeout'))

    def do_call(self, request, ep):
        return ep.call(request)

    def update_call_record(self, threshold_limit):
        if self.curRoundTotalCount > threshold_limit or (
                time_ns() - self.lastResetTime) >= counterScaleThreshold:
            self.curRoundTotalCount = 1
            self.curRoundRetryCount = 0
            self.lastResetTime = time_ns()
        else:
            self.curRoundTotalCount += 1

    def try_acquirePermit(self, threshold_limit):
        if self.curRoundRetryCount >= threshold_limit:
            return False
        self.curRoundRetryCount += 1
        return True
