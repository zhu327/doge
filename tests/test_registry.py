# coding: utf-8

import pytest
from gevent import sleep

from doge.registry.retcd import Registry

config = {"host": "127.0.0.1", "port": 2379, "ttl": 10}


@pytest.fixture(scope='function')
def registry():
    r = Registry(config)
    yield r
    if hasattr(r, 'beat_thread'):
        r.beat_thread.kill()
    if hasattr(r, 'watch_thread'):
        r.watch_thread.kill()


class TestRegistry(object):
    def teardown_method(self, method):
        if hasattr(self, 'registry'):
            self.registry.deregister(*self.args)
            del self.registry
            del self.args

    def test_register(self, registry):
        name, node, host, port = 'test', 'n1', 'locahost', '80'

        self.registry = registry
        self.args = [name, node]

        registry.register(name, node, host, port)
        res = registry.discovery(name)
        key = registry._node_key(name, node)
        assert key in res
        assert res[key] == ':'.join((host, port))

    def test_deregister(self, registry):
        name, node, host, port = 'test', 'n1', 'locahost', '80'

        registry.register(name, node, host, port)
        registry.deregister(name, node)
        res = registry.discovery(name)
        key = registry._node_key(name, node)
        assert not key in res

    def test_discovery(self, registry):
        name, node, host, port = 'test', 'n1', 'locahost', '80'

        self.registry = registry
        self.args = [name, node]

        self.registry = registry
        self.args = [name, node]

        registry.register(name, node, host, port)

        key = registry._node_key(name, 'n2')

        registry.etcd.write(key, ':'.join((host, '81')))

        res = registry.discovery(name)

        registry.etcd.delete(key)

        assert len(res) == 2

    def test_watch(self, registry):
        name, node, host, port = 'test', 'n1', 'locahost', '80'

        registry.register(name, node, host, port)

        def callback(res):
            print 'callback now'
            assert res['action'] == 'delete'

        registry.watch(name, callback)

        sleep(0.1)

        registry.deregister(name, node)
        registry.beat_thread.kill()
        sleep(0.1)
