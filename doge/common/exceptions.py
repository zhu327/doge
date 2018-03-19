# coding: utf-8


class DogeError(Exception):
    pass


class ServerLoadError(DogeError):
    pass


class RemoteError(DogeError):
    pass


class ClientError(DogeError):
    pass


class RegistryCfgError(DogeError):
    pass


class ServiceCfgError(DogeError):
    pass


class ReferCfgError(DogeError):
    pass