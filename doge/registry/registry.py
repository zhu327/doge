# coding: utf-8


class BaseRegistry(object):
    u"""注册中心

    与注册中心交互的实体

    *conf* 注册中心配置
        *host* 注册中心 host
        *port* 注册中心 port
    """

    def __init__(self, conf):
        self.conf = conf

    def register(self, name, node, host, port):
        u"""注册服务

        *name* 服务名称
        *node* 节点名称
        *host* 服务 host
        *port* 服务 port
        """
        raise NotImplementedError(
            'subclasses of Register may require a register() method')

    def discovery(self, name):
        u"""发现服务

        *name* 服务名称
        """
        raise NotImplementedError(
            'subclasses of Register may require a discovery() method')

    def watch(self, name, callback):
        u"""监听服务

        *name* 服务名称
        *callback* 通知的callback
        """
        raise NotImplementedError(
            'subclasses of Register may require a watch() method')

    def deregister(self, name, node):
        u"""去注册

        *name* 服务名称
        *node* 节点名称
        """
        raise NotImplementedError(
            'subclasses of Register may require a register() method')