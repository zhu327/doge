# coding: utf-8

from io import open

import yaml

from doge.common.exceptions import (
    ReferCfgError,
    RegistryCfgError,
    ServiceCfgError,
)
from doge.common.url import URL


class Config(object):
    def __init__(self, name: str) -> None:
        self.name = name
        self.cfg = self.config_from_file(name)

    def config_from_file(self, name: str):
        with open(name, "r", encoding="utf8") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def parse_registry(self) -> URL:
        if "registry" not in self.cfg:
            raise RegistryCfgError("registry config not exists")
        rcfg = self.cfg["registry"]
        if ("host" not in rcfg) and ("address" not in rcfg):
            raise RegistryCfgError("host or address must be provided")
        host = rcfg.get("host", None)
        port = rcfg.get("port", None)
        return URL(
            host and str(host) or host, port and int(port) or port, params=rcfg
        )

    def parse_service(self) -> URL:
        if "service" not in self.cfg:
            raise ServiceCfgError("service config not exists")
        scfg = self.cfg["service"]
        if ("host" not in scfg) or ("port" not in scfg):
            raise ServiceCfgError("host and port must be provided")
        if ("name" not in scfg) or ("node" not in scfg):
            raise ServiceCfgError("name and node must be provided")
        return URL(str(scfg["host"]), int(scfg["port"]), params=scfg)

    def parse_refer(self) -> URL:
        if "refer" not in self.cfg:
            raise ReferCfgError("refer config not exists")
        rcfg = self.cfg["refer"]
        return URL(None, None, params=rcfg)
