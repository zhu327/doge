# coding: utf-8

import time

import gevent
from gevent import socket
import gsocketpool.pool
from mprpc import RPCPoolClient
from mprpc.exceptions import RPCError, RPCProtocolError
from gsocketpool.exceptions import PoolExhaustedError

from doge.common.exceptions import RemoteError

defaultPoolSize = 3
defaultRequestTimeout = 1
defaultConnectTimeout = 1
defaultKeepaliveInterval = 10
defaultErrorCountThreshold = 10


class EndPoint(object):
    def __init__(self, address):
        self.address = address.split(':')
        self.available = True
        self.error_count = 0
        self.keepalive_count = 0
        self.pool = self.pool_factory()

    def pool_factory(self):
        return gsocketpool.pool.Pool(RPCPoolClient,
                                     dict(host=self.address[0],
                                          port=int(self.address[1]),
                                          timeout=defaultConnectTimeout,
                                          lifetime=defaultKeepaliveInterval,
                                          keep_alive=True),
                                     max_connections=defaultPoolSize)

    def call(self, *args):
        try:
            with self.pool.connection() as client:
                res = client.call(*args)
        except PoolExhaustedError:
            self.record_error()
            raise RemoteError('connection pool full')
        except (RPCError, RPCProtocolError) as e:
            raise RemoteError(e.message)
        except (IOError, socket.timeout):
            self.record_error()
            raise RemoteError('socket error or bad method')
        self.reset_error()
        return res

    def record_error(self):
        self.error_count += 1
        if self.error_count == defaultErrorCountThreshold:
            self.available = False
            gevent.spawn(self.keepalive)

    def keepalive(self):
        self.keepalive_count += 1

        start = time.time()
        while time.time() - start < defaultKeepaliveInterval:
            try:
                sock = socket.create_connection(
                    (self.address[0], int(self.address[1])),
                    defaultConnectTimeout)
            except:
                pass
            else:
                self.available = True
                self.reset_error()
                return
            finally:
                sock.close()

    def reset_error(self):
        self.error_count = 0

    def destroy(self):
        self.available = False
        del self.pool
