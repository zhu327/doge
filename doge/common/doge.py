# coding: utf-8

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Optional

from doge.common.url import URL


class Response(object):
    def __init__(
        self, value: Any = None, exception: Optional[Exception] = None,
    ) -> None:
        self.value = value
        self.exception = exception
        self.prosess_time = 0


class Request(object):
    def __init__(
        self, service: Optional[str], method: str, *args, meta=None
    ) -> None:
        self.service = service
        self.method = method
        self.args = args
        self.meta = meta or {}


class Executer(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, req: Request) -> Response:
        pass


class Registry(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, url: URL) -> None:
        self.url = url

    @abstractmethod
    def register(self, service, url):
        pass

    @abstractmethod
    def deregister(self, service, url):
        pass

    @abstractmethod
    def discovery(self, service: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def watch(self, service: str, callback: Callable) -> None:
        pass

    @abstractmethod
    def destroy(self) -> None:
        pass
