# coding: utf-8

import pytest
import gevent
from gevent import sleep

from mprpc import RPCClient

from doge.rpc.server import Server
from doge.common.context import Context
from doge.common.url import URL

url = URL("127.0.0.1", 4399, params={"name": "test", "node": "n1"})
rurl = URL("127.0.0.1", 2379, params={"ttl": 10})
context = Context(url, rurl)


@pytest.fixture(scope="function")
def server():
    s = Server(context)
    yield s
    s.registry.deregister(s.name, url)
    s.registry.destroy()


class TestServer(object):
    def teardown_method(self, method):
        self.g.kill()

    def test_server(self, server):
        class Sum(object):
            def sum(self, x, y):
                return x + y

        server.load(Sum)
        self.g = gevent.spawn(server.run)
        sleep(0.1)

        registry = server.registry
        res = registry.discovery(server.name)
        key = registry._node_key(server.name, url.get_param("node"))

        host, port = res[key].split(":")

        client = RPCClient(str(host), int(port))

        assert client.call("sum", {}, 1, 2) == 3
