# coding: utf-8


from typing import Any, Optional

from doge.common.exceptions import DogeError


class Response(object):
    def __init__(
        self, value: Any = None, exception: Optional[DogeError] = None,
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
