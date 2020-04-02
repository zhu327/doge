# coding: utf-8

import time

from typing import Union

import gevent  # type: ignore
from gevent import socket  # type: ignore
from gsocketpool.exceptions import PoolExhaustedError  # type: ignore
from mprpc import RPCPoolClient  # type: ignore
from mprpc.exceptions import RPCError, RPCProtocolError  # type: ignore

from doge.common.doge import Request, Response
from doge.common.exceptions import RemoteError
from doge.common.url import URL
from doge.common.utils import ConnPool

defaultPoolSize = 3
defaultRequestTimeout = 1
defaultConnectTimeout = 1
defaultKeepaliveInterval = 10
defaultErrorCountThreshold = 10


class EndPoint(object):
    def __init__(self, url: URL) -> None:
        self.url = url
        self.available = True
        self.error_count = 0
        self.keepalive_count = 0
        self.pool = self.pool_factory()

    def pool_factory(self) -> ConnPool:
        return ConnPool(
            RPCPoolClient,
            dict(
                host=self.url.host,
                port=self.url.port,
                timeout=defaultConnectTimeout,
                keep_alive=True,
            ),
            max_connections=defaultPoolSize,
            reap_expired_connections=False,
        )

    def call(self, request: Request) -> Response:
        try:
            with self.pool.connection() as client:
                if not client.is_connected():
                    client.open()
                res = client.call(request.method, request.meta, *request.args)
        except PoolExhaustedError:
            self.record_error()
            return Response(exception=RemoteError("connection pool full"))
        except (RPCError, RPCProtocolError) as e:
            return Response(exception=RemoteError(str(e)))
        except (IOError, socket.timeout):
            self.record_error()
            return Response(
                exception=RemoteError("socket error or bad method")
            )
        self.reset_error()
        return Response(value=res)

    def record_error(self) -> None:
        self.error_count += 1
        if self.error_count == defaultErrorCountThreshold:
            self.available = False
            gevent.spawn(self.keepalive)

    def keepalive(self):
        self.keepalive_count += 1

        start = time.time()
        while time.time() - start < defaultKeepaliveInterval:
            sock = None
            try:
                sock = socket.create_connection(
                    (self.url.host, self.url.port), defaultConnectTimeout
                )
            except Exception:
                pass
            else:
                self.available = True
                self.reset_error()
                return
            finally:
                if sock:
                    sock.close()

    def reset_error(self) -> None:
        self.error_count = 0

    def destroy(self) -> None:
        self.available = False
        del self.pool


def new_endpoint(k: Union[int, str], v: str) -> EndPoint:
    host, port = v.split(":")
    url = URL(str(host), int(port), k)
    return EndPoint(url)
