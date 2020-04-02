# coding: utf-8

from __future__ import print_function

import logging

import gevent
from gevent import monkey

from doge.common.utils import init_tracer
from doge.rpc.client import Cluster

monkey.patch_socket()


logging.basicConfig(level=logging.DEBUG)


init_tracer("client")  # 初始化jaeger tracer

if __name__ == "__main__":
    cluster = Cluster("client.yaml")  # 基于配置文件实例化Cluster对象
    client = cluster.get_client("doge_server")  # 获取服务名对应的Client对象
    print(client.call("sum", 1, 2))  # 远程调用服务Sum类下的sum方法
    gevent.sleep(2)  # wait for jaeger report
