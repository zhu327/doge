# coding: utf-8

reuse_port = True
worker_class = "doge.gunicorn.worker.DogeWorker"


def when_ready(server):
    server.app.wsgi().register()


def on_exit(server):
    app = server.app.wsgi()
    app.registry.deregister(app.name, app.url)
