# coding: utf-8


class DogeError(Exception):
    pass


class ServerLoadError(DogeError):
    pass


class RemoteError(DogeError):
    pass


class ClientError(DogeError):
    pass
