# coding: utf-8

from gunicorn.workers.ggevent import GeventWorker  # type: ignore


class DogeWorker(GeventWorker):
    u""" 适用于Doge的Gunicorn Worker
    """

    def handle(self, listener, client, addr):
        client.setblocking(1)
        self.wsgi.handler(client, addr)
