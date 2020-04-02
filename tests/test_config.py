# coding: utf-8

import os

import gevent

from doge.rpc.client import Cluster
from doge.rpc.server import new_server


class Sum(object):
    def sum(self, x, y):
        return x + y


class TestConfig(object):
    def teardown_method(self, method):
        self.g.kill()
        self.server.registry.deregister(
            self.server.name, self.server.context.url)
        self.server.registry.destroy()
        self.client.destroy()

    def test_config(self):
        cpath = os.path.join(os.path.dirname(__file__), "client.yaml")
        spath = os.path.join(os.path.dirname(__file__), "server.yaml")
        cluster = Cluster(cpath)
        server = new_server(spath)
        server.load(Sum)
        self.server = server
        self.g = gevent.spawn(server.run)
        gevent.sleep(0.1)
        cluster = Cluster(cpath)
        client = cluster.get_client("test")
        self.client = client
        assert client.call("sum", 1, 2)
