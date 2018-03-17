# coding: utf-8

import logging
import signal

from gevent.server import StreamServer
from mprpc import RPCServer

from doge.common.utils import import_string
from doge.common.exceptions import ServerLoadError

logger = logging.getLogger('doge.rpc.server')


class Server(object):
    def __init__(self, conf):
        self.conf = conf
        self.registry = None
        self.handler = None

        self.init()

    def init(self):
        u"""初始化registry"""
        conf = self.conf['registry']

        cls = import_string(conf['registry_class'])
        self.registry = cls(conf)

    def load(self, cls):
        u"""加载RPC methods类"""

        class RPC(RPCServer, cls):
            def __init__(self):
                RPCServer.__init__(self)
                cls.__init__(self)

        self.handler = RPC()

    def register(self):
        u"""向registry服务"""
        conf = self.conf

        self.registry.register(conf['name'], conf['node'], conf['host'],
                               conf['port'])

    def handle_signal(self):
        u"""注册信号"""
        conf = self.conf

        def handler(signum, frame):
            self.registry.deregister(conf['name'], conf['node'])

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def run(self):
        u"""启动RPC服务"""
        if not self.handler:
            raise ServerLoadError('Methods not exits.')

        conf = self.conf

        logger.info("Starting server at %s:%s" % (conf['host'], conf['port']))

        self.handle_signal()

        server = StreamServer((conf['host'], conf['port']), self.handler)

        self.register()

        server.serve_forever()
