# coding: utf-8

from __future__ import print_function

from gevent import monkey
monkey.patch_socket()

import logging
logging.basicConfig(level=logging.DEBUG)

from doge.rpc.client import Cluster

if __name__ == '__main__':
    cluster = Cluster('client.json')  # 基于配置文件实例化Cluster对象
    client = cluster.get_client("test")  # 获取服务名对应的Client对象
    print(client.call('sum', 1, 2))  # 远程调用服务Sum类下的sum方法
