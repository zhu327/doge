# coding: utf-8

import json
from io import open

from doge.common.url import URL
from doge.common.exceptions import (RegistryCfgError, ServiceCfgError,
                                    ReferCfgError)


class Config(object):
    def __init__(self, name):
        self.name = name
        self.cfg = self.config_from_file(name)

    def config_from_file(self, name):
        with open(name, 'r', encoding='utf8') as f:
            content = f.read()
        return json.loads(content)

    def parse_registry(self):
        if not 'registry' in self.cfg:
            raise RegistryCfgError("registry config not exists")
        rcfg = self.cfg['registry']
        if (not 'host' in rcfg) and (not 'address' in rcfg):
            raise RegistryCfgError("host or address must be provided")
        host = rcfg.get('host', None)
        port = rcfg.get('port', None)
        return URL(
            host and str(host) or host,
            port and int(port) or port,
            params=rcfg)

    def parse_service(self):
        if not 'service' in self.cfg:
            raise ServiceCfgError("service config not exists")
        scfg = self.cfg['service']
        if (not 'host' in scfg) or (not 'port' in scfg):
            raise ServiceCfgError("host and port must be provided")
        if (not 'name' in scfg) or (not 'node' in scfg):
            raise ServiceCfgError("name and node must be provided")
        return URL(str(scfg['host']), int(scfg['port']), params=scfg)

    def parse_refer(self):
        if not 'refer' in self.cfg:
            raise ReferCfgError("refer config not exists")
        rcfg = self.cfg['refer']
        return URL(None, None, params=rcfg)
