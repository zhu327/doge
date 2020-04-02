# coding: utf-8

from __future__ import print_function
import pytest
from gevent import sleep

from doge.registry.registry import EtcdRegistry, DirectRegistry
from doge.common.url import URL

url = URL("127.0.0.1", 2379, params={"ttl": 10})


@pytest.fixture(scope="function")
def registry():
    return EtcdRegistry(url)


class TestEtcdRegistry(object):
    def teardown_method(self, method):
        if hasattr(self, "registry"):
            self.registry.deregister(*self.args)
            self.registry.destroy()
            del self.registry
            del self.args

    def test_register(self, registry):
        service = "test"
        url = URL("locahost", 80, params={"node": "n1"})

        self.registry = registry
        self.args = [service, url]

        registry.register(service, url)
        res = registry.discovery(service)
        key = registry._node_key(service, url.get_param("node"))
        assert key in res
        assert res[key] == ":".join((url.host, str(url.port)))

    def test_deregister(self, registry):
        service = "test"
        url = URL("locahost", 80, params={"node": "n1"})

        registry.register(service, url)
        registry.deregister(service, url)
        res = registry.discovery(service)
        key = registry._node_key(service, url.get_param("node"))
        assert key not in res

    def test_discovery(self, registry):
        service = "test"
        url = URL("locahost", 80, params={"node": "n1"})

        self.registry = registry
        self.args = [service, url]

        registry.register(service, url)

        key = registry._node_key(service, "n2")

        registry.etcd.write(key, ":".join((url.host, "81")))

        res = registry.discovery(service)

        registry.etcd.delete(key)

        assert len(res) == 2

    def test_watch(self, registry):
        service = "test_watch"
        url = URL("locahost", 80, params={"node": "n1"})

        registry.register(service, url)

        sleep(0.1)

        def callback(res):
            print("callback now")
            assert res["action"] == "delete"

        registry.watch(service, callback)

        sleep(0.1)

        registry.deregister(service, url)
        registry.beat_thread.kill()
        sleep(0.1)

    def test_zaddress(self):
        service = "test"
        url = URL("locahost", 80, params={"node": "n1"})

        rurl = URL(None, None, params={"ttl": 10, "address": "127.0.0.1:2379"})

        registry = EtcdRegistry(rurl)
        self.registry = registry
        self.args = [service, url]

        registry.register(service, url)
        res = registry.discovery(service)
        key = registry._node_key(service, url.get_param("node"))
        assert key in res
        assert res[key] == ":".join((url.host, str(url.port)))


class TestDirectRegistry(object):
    def test_direct(self):
        registry = DirectRegistry(url)
        assert registry.discovery("")["0"] == "127.0.0.1:2379"
