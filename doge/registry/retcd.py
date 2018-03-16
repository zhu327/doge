# coding: utf-8

import logging

import gevent
import etcd

from registry import BaseRegistry

logger = logging.getLogger('doge.registry.etcd')


class Registry(BaseRegistry):
    """Register etcd"""

    def __init__(self, conf):
        super(Registry, self).__init__(conf)
        self.etcd = etcd.Client(host=conf['host'], port=conf['port'])

    def register(self, name, node, host, port):
        n_key = self._node_key(name, node)
        value = '{}:{}'.format(host, port)
        ttl = self.conf.get('ttl', 10)

        logger.info("register key: %s value: %s" % (n_key, value))

        self.heartbeat(n_key, value, ttl=ttl)

    def deregister(self, name, node):
        n_key = self._node_key(name, node)

        logger.debug("deregister key: %s" % n_key)

        self.etcd.delete(n_key)

    def discovery(self, name):
        s_key = self._svc_key(name)
        res = self.etcd.read(s_key, recursive=True)

        logger.info("discovery key: %s length: %s" %
                    (s_key, len(res._children)))

        return {child.key: child.value for child in res.children}

    def watch(self, name, callback):
        def watch_loop():
            s_key = self._svc_key(name)
            while 1:
                try:
                    res = self.etcd.watch(s_key, recursive=True)
                    callback({'action': self._proc_action(res.action),
                              'key': res.key,
                              'value': res.value})
                except etcd.EtcdWatchTimedOut:
                    pass

        self.watch_thread = gevent.spawn(watch_loop)

    def _proc_action(self, action):
        return 'delete' if action == 'expire' else action

    def _svc_key(self, name):
        return '/doge/rpc/{}'.format(name)

    def _node_key(self, name, node):
        return '/doge/rpc/{}/{}'.format(name, node)

    def heartbeat(self, key, value, ttl):
        self.etcd.write(key, value, ttl=ttl)

        def heartbeat_loop():
            sleep = int(ttl / 2)
            while 1:
                gevent.sleep(sleep)
                self.etcd.refresh(key, ttl)

        self.beat_thread = gevent.spawn(heartbeat_loop)