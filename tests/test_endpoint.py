# coding: utf-8

import gevent
import pytest

from gevent.server import StreamServer
from mprpc import RPCServer

from doge.cluster.endpoint import EndPoint


class SumServer(RPCServer):
    def sum(self, x, y):
        return x + y


@pytest.fixture(scope='function')
def server():
    server = StreamServer(('127.0.0.1', 4399), SumServer())
    g = gevent.spawn(server.serve_forever)
    gevent.sleep(0.1)
    yield server
    g.kill()


class TestEndpoint(object):
    def teardown_method(self, method):
        if hasattr(self, 'ep'):
            self.ep.destroy()
            del self.ep

    def test_endpoint(self, server):
        ep = EndPoint('127.0.0.1:4399')
        self.ep = ep
        assert ep.call('sum', 1, 2) == 3

    def test_error(self, server):
        ep = EndPoint('127.0.0.1:4399')
        self.ep = ep
        availables = []
        for i in range(11):
            try:
                ep.call('a')
            except:
                availables.append(ep.available)
        assert False in availables
        gevent.sleep(0.2)
        assert ep.available
        assert ep.call('sum', 1, 2) == 3
