# coding: utf-8

import os, sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.getcwd())))

from gevent import monkey
monkey.patch_socket()

import logging
logging.basicConfig(level=logging.DEBUG)

config = {
    "name": "demo",
    "node": "n1",
    "host": "127.0.0.1",
    "port": 4399,
    "registry": {
        "registry_class": "doge.registry.retcd.Registry",
        "host": "127.0.0.1",
        "port": 2379,
        "ttl": 10
    }
}

from doge.rpc.server import Server


class Sum(object):
    def sum(self, x, y):
        return x + y


if __name__ == '__main__':
    server = Server(config)
    server.load(Sum)
    server.run()