# coding: utf-8

from doge.registry.registry import EtcdRegistry, DirectRegistry
from doge.cluster.ha import FailOverHA, BackupRequestHA
from doge.cluster.lb import RandomLB, RoundrobinLB
from doge.cluster.endpoint import EndPoint
from doge.common.url import URL


class Context(object):
    def __init__(self, url, registry_url):
        self.url = url
        self.registry_url = registry_url

    def get_registry(self):
        protocol = self.registry_url.get_param("protocol", "etcd")
        if protocol == "etcd":
            return EtcdRegistry(self.registry_url)
        elif protocol == "direct":
            return DirectRegistry(self.registry_url)

    def get_endpoints(self, registry, service):
        eps = {}
        for k, v in registry.discovery(service).items():
            eps[k] = new_endpoint(k, v)
        return eps

    def get_ha(self):
        name = self.url.get_param("haStrategy", "failover")
        if name == "failover":
            return FailOverHA(self.url)
        elif name == "backupRequestHA":
            return BackupRequestHA(self.url)

    def get_lb(self, eps):
        name = self.url.get_param("loadBalance", "RoundrobinLB")
        if name == "RandomLB":
            return RandomLB(self.url, eps)
        elif name == "RoundrobinLB":
            return RoundrobinLB(self.url, eps)


def new_endpoint(k, v):
    host, port = v.split(":")
    url = URL(str(host), int(port), k)
    return EndPoint(url)
