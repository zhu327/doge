# coding: utf-8

import gevent
import pytest

from gevent.server import StreamServer

from doge.cluster.endpoint import EndPoint
from doge.common.url import URL
from doge.common.doge import Request
from doge.rpc.server import DogeRPCServer
from doge.common.context import Context


class SumServer(object):
    def sum(self, x, y):
        return x + y


@pytest.fixture(scope="function")
def server():
    server = StreamServer(
        ("127.0.0.1", 4399),
        DogeRPCServer(
            Context(
                URL(None, None, None, {"name": ""}), URL(None, None, None, {})
            ),
            SumServer,
        ),
    )
    g = gevent.spawn(server.serve_forever)
    gevent.sleep(0.1)
    yield server
    g.kill()


@pytest.fixture(scope="module")
def url():
    return URL("127.0.0.1", 4399, "")


class TestEndpoint(object):
    def teardown_method(self, method):
        if hasattr(self, "ep"):
            self.ep.destroy()
            del self.ep

    def test_endpoint(self, server, url):
        ep = EndPoint(url)
        self.ep = ep
        r = Request("", "sum", 1, 2)
        assert ep.call(r).value == 3

    def test_error(self, server, url):
        ep = EndPoint(url)
        self.ep = ep
        availables = []
        r = Request("", "a")
        for i in range(11):
            ep.call(r)
            availables.append(ep.available)
        assert False in availables
        gevent.sleep(0.2)
        assert ep.available
        r = Request("", "sum", 1, 2)
        assert ep.call(r).value == 3
