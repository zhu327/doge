# coding: utf-8

import pytest
import gevent
from gevent import sleep

from mprpc import RPCClient

from doge.rpc.server import Server

config = {
    "name": "test",
    "node": "n1",
    "host": "127.0.0.1",
    "port": 4399,
    "registry": {
        "registry_class": "doge.registry.retcd.Registry",
        "host": "127.0.0.1",
        "port": 6001,
        "ttl": 10
    }
}


@pytest.fixture(scope='function')
def server():
    s = Server(config)
    yield s
    s.registry.deregister(config['name'], config['node'])
    s.registry.beat_thread.kill()


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
        res = registry.discovery(config['name'])
        key = registry._node_key(config['name'], config['node'])

        host, port = res[key].split(':')

        client = RPCClient(config['host'], config['port'])

        assert client.call('sum', 1, 2) == 3
