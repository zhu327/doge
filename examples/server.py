# coding: utf-8

from gevent import monkey

monkey.patch_socket()

import logging

logging.basicConfig(level=logging.DEBUG)

from doge.rpc.server import new_server
from doge.common.utils import init_tracer

init_tracer("server")


# 定义rpc方法类
class Sum(object):
    def sum(self, x, y):
        return x + y


if __name__ == "__main__":
    server = new_server("server.json")  # 基于配置文件实例化server对象
    server.load(Sum)  # 加载暴露rpc方法类
    server.run()  # 启动服务并注册节点信息到注册中心
