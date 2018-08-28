# coding: utf-8

from gunicorn.workers.ggevent import GeventWorker


class DogeWorker(GeventWorker):
    u""" 适用于Doge的Gunicorn Worker
    """
    def handle(self, listener, client, addr):
        self.wsgi.handler(client, addr)
