# coding: utf-8

import pytest
from gevent import sleep

from doge.registry.registry import Registry
from doge.common.url import URL

url = URL("127.0.0.1", 2379, params={"ttl": 10})


@pytest.fixture(scope='function')
def registry():
    r = Registry(url)
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
        service = 'test'
        url = URL('locahost', 80, params={"node": 'n1'})

        self.registry = registry
        self.args = [service, url]

        registry.register(service, url)
        res = registry.discovery(service)
        key = registry._node_key(service, url.get_param("node"))
        assert key in res
        assert res[key] == ':'.join((url.host, str(url.port)))

    def test_deregister(self, registry):
        service = 'test'
        url = URL('locahost', 80, params={"node": 'n1'})

        registry.register(service, url)
        registry.deregister(service, url)
        res = registry.discovery(service)
        key = registry._node_key(service, url.get_param("node"))
        assert not key in res

    def test_discovery(self, registry):
        service = 'test'
        url = URL('locahost', 80, params={"node": 'n1'})

        self.registry = registry
        self.args = [service, url]

        registry.register(service, url)

        key = registry._node_key(service, 'n2')

        registry.etcd.write(key, ':'.join((url.host, '81')))

        res = registry.discovery(service)

        registry.etcd.delete(key)

        assert len(res) == 2

    def test_watch(self, registry):
        service = 'test'
        url = URL('locahost', 80, params={"node": 'n1'})

        registry.register(service, url)

        def callback(res):
            print 'callback now'
            assert res['action'] == 'delete'

        registry.watch(service, callback)

        sleep(0.1)

        registry.deregister(service, url)
        registry.beat_thread.kill()
        sleep(0.1)
