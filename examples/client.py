# coding: utf-8

from __future__ import print_function
import time

from gevent import monkey

monkey.patch_socket()

import logging

logging.basicConfig(level=logging.DEBUG)

import gevent
from doge.rpc.client import Cluster
from doge.common.utils import init_tracer

init_tracer("client")  # 初始化jaeger tracer

if __name__ == "__main__":
    cluster = Cluster("client.json")  # 基于配置文件实例化Cluster对象
    client = cluster.get_client("doge_server")  # 获取服务名对应的Client对象
    print(client.call("sum", 1, 2))  # 远程调用服务Sum类下的sum方法
    gevent.sleep(2)  # wait for jaeger report
