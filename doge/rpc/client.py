# coding: utf-8

import logging

from gevent.lock import BoundedSemaphore

from doge.common.doge import Request
from doge.common.exceptions import ClientError
from doge.rpc.context import new_endpoint, Context
from doge.config.config import Config

logger = logging.getLogger('doge.rpc.client')


class Client(object):
    def __init__(self, context, service):
        self.service = service
        self.url = context.url
        self.context = context
        self.regisry = context.get_registry()
        self.endpoints = context.get_endpoints(self.regisry, service)
        self.ha = context.get_ha()
        self.lb = context.get_lb(list(self.endpoints.values()))
        self.available = True
        self.closed = False

        self.watch()

    def call(self, method, *args):
        if self.available:
            r = Request(self.service, method, *args)
            res = self.ha.call(r, self.lb)
            if res.exception:
                logger.error(str(res.exception))
                raise res.exception
            return res.value
        raise ClientError("client not available")

    def watch(self):
        self.regisry.watch(self.service, self.notify)

    def notify(self, event):
        if event['action'] == 'delete':
            ep = self.endpoints[event['key']]
            self.lb.endpoints.remove(ep)
            del self.endpoints[event['key']]
        elif event['action'] == 'set':
            ep = new_endpoint(event['key'], event['value'])
            self.endpoints[event['key']] = ep
            self.lb.endpoints.append(ep)

    def destroy(self):
        if not self.closed:
            self.closed = True
            self.regisry.destroy()
            for k, v in self.endpoints.items():
                v.destroy()
            del self.context
            del self.regisry
            del self.ha
            del self.endpoints
            del self.lb
            self.closed = True


class Cluster(object):
    def __init__(self, config_file):
        u"""Cluster 抽象"""
        self.config_file = config_file
        self.config = Config(config_file)
        self.context = Context(self.config.parse_refer(),
                               self.config.parse_registry())

        self.clients = {}
        self.sem = BoundedSemaphore(1)

    def get_client(self, service):
        if not service in self.clients:
            self.sem.acquire()
            if not service in self.clients:
                self.clients[service] = Client(self.context, service)
            self.sem.release()
        return self.clients[service]