# coding: utf-8

import logging
from typing import Any, Dict

from gevent.lock import BoundedSemaphore  # type: ignore

from doge.common.doge import Executer, Request, Response
from doge.common.exceptions import ClientError
from doge.config.config import Config
from doge.common.context import Context
from doge.cluster.endpoint import new_endpoint

logger = logging.getLogger("doge.rpc.client")


class Client(Executer):
    def __init__(self, context: Context, service: str) -> None:
        self.service = service
        self.url = context.url
        self.context = context
        self.registry = context.get_registry()
        self.endpoints = context.get_endpoints(self.registry, service)
        self.ha = context.get_ha()
        self.lb = context.get_lb(list(self.endpoints.values()))
        self.filter = context.get_filter(self)
        self.available = True
        self.closed = False

        self.watch()

    def call(self, method: str, *args) -> Any:
        if self.available:
            r = Request(self.service, method, *args)
            res = self.filter.execute(r)
            if res.exception:
                logger.error(str(res.exception))
                raise res.exception
            return res.value
        raise ClientError("client not available")

    def execute(self, req: Request) -> Response:
        return self.ha.call(req, self.lb)

    def watch(self) -> None:
        self.registry.watch(self.service, self.notify)

    def notify(self, event: Dict[str, Any]) -> None:
        if event["action"] == "delete":
            ep = self.endpoints[event["key"]]
            self.lb.endpoints.remove(ep)
            del self.endpoints[event["key"]]
        elif event["action"] == "set":
            ep = new_endpoint(event["key"], event["value"])
            self.endpoints[event["key"]] = ep
            self.lb.endpoints.append(ep)

    def destroy(self) -> None:
        if not self.closed:
            self.closed = True
            self.registry.destroy()
            for k, v in self.endpoints.items():
                v.destroy()
            del self.context
            del self.registry
            del self.ha
            del self.endpoints
            del self.lb
            self.closed = True


class Cluster(object):
    def __init__(self, config_file: str) -> None:
        u"""Cluster 抽象"""
        self.config_file = config_file
        self.config = Config(config_file)
        self.context = Context(
            self.config.parse_refer(), self.config.parse_registry()
        )

        self.clients: Dict[str, Client] = {}
        self.sem = BoundedSemaphore(1)

    def get_client(self, service: str) -> Client:
        if service not in self.clients:
            self.sem.acquire()
            if service not in self.clients:
                self.clients[service] = Client(self.context, service)
            self.sem.release()
        return self.clients[service]
