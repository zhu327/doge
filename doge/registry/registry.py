# coding: utf-8

import logging

import gevent
import etcd

from doge.common.utils import str_to_host

logger = logging.getLogger('doge.registry.etcd')


class EtcdRegistry(object):
    """Register etcd"""

    def __init__(self, url):
        self.url = url
        self.etcd = self.registry_factory(url)

    def registry_factory(self, url):
        address = url.get_param("address")
        if address:
            return etcd.Client(
                allow_reconnect=True,
                host=tuple([str_to_host(add) for add in address.split(",")]))
        return etcd.Client(host=url.host, port=url.port)

    def register(self, service, url):
        n_key = self._node_key(service, url.get_param('node'))
        value = '{}:{}'.format(url.host, url.port)
        ttl = self.url.get_param('ttl', 10)

        logger.info("register key: %s value: %s" % (n_key, value))

        self.heartbeat(n_key, value, ttl=ttl)

    def deregister(self, service, url):
        n_key = self._node_key(service, url.get_param('node'))

        logger.debug("deregister key: %s" % n_key)

        self.etcd.delete(n_key)

    def discovery(self, service):
        s_key = self._svc_key(service)
        res = self.etcd.read(s_key, recursive=True)

        logger.info("discovery key: %s length: %s" %
                    (s_key, len(res._children)))

        return {child.key: child.value for child in res.children}

    def watch(self, service, callback):
        def watch_loop():
            s_key = self._svc_key(service)
            for res in self.etcd.eternal_watch(s_key, recursive=True):
                callback({
                    'action': self._proc_action(res.action),
                    'key': res.key,
                    'value': res.value
                })

        self.watch_thread = gevent.spawn(watch_loop)

    def _proc_action(self, action):
        return 'delete' if action == 'expire' else action

    def _svc_key(self, service):
        return '/doge/rpc/{}'.format(service)

    def _node_key(self, service, node):
        return '/doge/rpc/{}/{}'.format(service, node)

    def heartbeat(self, key, value, ttl):
        self.etcd.write(key, value, ttl=ttl)

        def heartbeat_loop():
            sleep = int(ttl / 2)
            while 1:
                gevent.sleep(sleep)
                self.etcd.refresh(key, ttl)

        self.beat_thread = gevent.spawn(heartbeat_loop)

    def destroy(self):
        if hasattr(self, "beat_thread"):
            self.beat_thread.kill()
        if hasattr(self, "watch_thread"):
            self.watch_thread.kill()


class DirectRegistry(object):
    """Fake Registry"""

    def __init__(self, url):
        self.url = url

    def register(self, service, url):
        pass

    def deregister(self, service, url):
        pass

    def discovery(self, service):
        address = self.url.get_param("address")
        if address:
            return {i: add for i, add in enumerate(address.split(","))}
        return {0: "%s:%s" % (self.url.host, str(self.url.port))}

    def watch(self, service, callback):
        pass

    def destroy(self):
        pass
