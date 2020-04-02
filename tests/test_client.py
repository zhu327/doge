# coding: utf-8

import pytest
import gevent
from gevent import sleep

from doge.rpc.server import Server
from doge.common.context import Context
from doge.common.url import URL
from doge.rpc.client import Client
from doge.common.exceptions import RemoteError

url = URL("127.0.0.1", 4399, params={"name": "test", "node": "n1"})
rurl = URL("127.0.0.1", 2379, params={"ttl": 10})
context = Context(url, rurl)


class Sum(object):
    def sum(self, x, y):
        return x + y


@pytest.fixture(scope="module")
def server():
    s = Server(context)
    s.load(Sum)
    g = gevent.spawn(s.run)
    sleep(0.1)
    yield s
    g.kill()
    s.registry.destroy()


class TestClient(object):
    def teardown_method(self, method):
        self.c.destroy()
        del self.c

    def test_client(self, server):
        c = Client(context, "test")
        self.c = c
        assert c.call("sum", 1, 2) == 3
        assert c.call("sum", 1, 2) == 3
        assert c.call("sum", 1, 2) == 3
        c.registry.deregister(c.service, url)
        sleep(0.2)
        with pytest.raises(RemoteError):
            c.call("sum", 1, 2)

    def test_context(self, server):
        url = URL(
            "127.0.0.1",
            4399,
            params={
                "name": "test",
                "node": "n1",
                "haStrategy": "backupRequestHA",
                "loadBalance": "RandomLB",
            },
        )
        rurl = URL("127.0.0.1", 4399, params={"protocol": "direct"})
        context = Context(url, rurl)
        c = Client(context, "test")
        self.c = c
        assert c.call("sum", 1, 2) == 3
        assert c.call("sum", 1, 2) == 3
        assert c.call("sum", 1, 2) == 3
