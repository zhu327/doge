# coding: utf-8

import logging
from typing import Callable, Dict

import etcd  # type: ignore
import gevent  # type: ignore
from etcd.client import Client  # type: ignore

from doge.common.url import URL
from doge.common.utils import str_to_host
from doge.common.doge import Registry

logger = logging.getLogger("doge.registry.etcd")


class EtcdRegistry(Registry):
    """Register etcd"""

    def __init__(self, url: URL) -> None:
        self.url = url
        self.etcd = self.registry_factory(url)

    def registry_factory(self, url: URL) -> Client:
        address = url.get_param("address")
        if address:
            return etcd.Client(
                allow_reconnect=True,
                host=tuple([str_to_host(add) for add in address.split(",")]),
            )
        return etcd.Client(host=url.host, port=url.port)

    def register(self, service: str, url: URL) -> None:
        n_key = self._node_key(service, url.get_param("node"))
        value = "{}:{}".format(url.host, url.port)
        ttl = self.url.get_param("ttl", 10)

        logger.info("register key: %s value: %s" % (n_key, value))

        self.heartbeat(n_key, value, ttl=ttl)

    def deregister(self, service: str, url: URL) -> None:
        n_key = self._node_key(service, url.get_param("node"))

        logger.debug("deregister key: %s" % n_key)

        self.etcd.delete(n_key)

    def discovery(self, service: str) -> Dict[str, str]:
        s_key = self._svc_key(service)
        res = self.etcd.read(s_key, recursive=True)

        logger.info(
            "discovery key: %s length: %s" % (s_key, len(res._children))
        )

        return {child.key: child.value for child in res.children}

    def watch(self, service: str, callback: Callable) -> None:
        def watch_loop():
            s_key = self._svc_key(service)
            for res in self.etcd.eternal_watch(s_key, recursive=True):
                callback(
                    {
                        "action": self._proc_action(res.action),
                        "key": res.key,
                        "value": res.value,
                    }
                )

        self.watch_thread = gevent.spawn(watch_loop)

    def _proc_action(self, action: str) -> str:
        return "delete" if action == "expire" else action

    def _svc_key(self, service: str) -> str:
        return "/doge/rpc/{}".format(service)

    def _node_key(self, service: str, node: str) -> str:
        return "/doge/rpc/{}/{}".format(service, node)

    def heartbeat(self, key: str, value: str, ttl: int) -> None:
        self.etcd.write(key, value, ttl=ttl)

        def heartbeat_loop():
            sleep = int(ttl / 2)
            while 1:
                gevent.sleep(sleep)
                self.etcd.refresh(key, ttl)

        self.beat_thread = gevent.spawn(heartbeat_loop)

    def destroy(self) -> None:
        if hasattr(self, "beat_thread"):
            self.beat_thread.kill()
        if hasattr(self, "watch_thread"):
            self.watch_thread.kill()


class DirectRegistry(Registry):
    """Fake Registry"""

    def __init__(self, url: URL) -> None:
        self.url = url

    def register(self, service, url):
        pass

    def deregister(self, service, url):
        pass

    def discovery(self, service: str) -> Dict[str, str]:
        address = self.url.get_param("address")
        if address:
            return {str(i): add for i, add in enumerate(address.split(","))}
        return {"0": "%s:%s" % (self.url.host, str(self.url.port))}

    def watch(self, service: str, callback: Callable) -> None:
        pass

    def destroy(self) -> None:
        pass
