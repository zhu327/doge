# coding: utf-8

import time

import gevent
from gevent import socket
import gsocketpool.pool
from mprpc import RPCPoolClient
from mprpc.exceptions import RPCError, RPCProtocolError
from gsocketpool.exceptions import PoolExhaustedError

from doge.common.doge import Response
from doge.common.exceptions import RemoteError

defaultPoolSize = 3
defaultRequestTimeout = 1
defaultConnectTimeout = 1
defaultKeepaliveInterval = 10
defaultErrorCountThreshold = 10


class EndPoint(object):
    def __init__(self, url):
        self.url = url
        self.available = True
        self.error_count = 0
        self.keepalive_count = 0
        self.pool = self.pool_factory()

    def pool_factory(self):
        return gsocketpool.pool.Pool(RPCPoolClient,
                                     dict(host=self.url.host,
                                          port=self.url.port,
                                          timeout=defaultConnectTimeout,
                                          lifetime=defaultKeepaliveInterval,
                                          keep_alive=True),
                                     max_connections=defaultPoolSize)

    def call(self, request):
        try:
            with self.pool.connection() as client:
                res = client.call(request.method, *request.args)
        except PoolExhaustedError:
            self.record_error()
            return Response(exception=RemoteError('connection pool full'))
        except (RPCError, RPCProtocolError) as e:
            return Response(exception=RemoteError(e.message))
        except (IOError, socket.timeout):
            self.record_error()
            return Response(
                exception=RemoteError('socket error or bad method'))
        self.reset_error()
        return Response(value=res)

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
                    (self.url.host, self.url.port), defaultConnectTimeout)
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