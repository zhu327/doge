# coding: utf-8


from typing import Any, Optional, Union


class URL(object):
    def __init__(
        self,
        host: Optional[str],
        port: Optional[Union[int, str]],
        path: Optional[Union[int, str]] = "",
        params: Optional[Any] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.path = path
        self.params = params or {}

    def get_int(self, key: str) -> Optional[int]:
        if key in self.params and isinstance(self.params[key], int):
            return self.params[key]
        return None

    def get_int_value(self, key: str, default: int) -> int:
        value = self.get_int(key)
        return value or default

    def get_positive_int_value(self, key: str, default: int) -> int:
        value = self.get_int_value(key, default)
        return default if value < 1 else value

    def get_param(self, key: str, default: Any = None) -> Any:
        if key in self.params and self.params[key]:
            return self.params[key]
        return default

    def get_method_int_value(self, method: str, key: str, default: int) -> int:
        mkey = "".join([method, ".", key])
        value = self.get_int(mkey)
        return value or default

    def get_method_positive_int_value(
        self, method: str, key: str, default: int
    ) -> int:
        value = self.get_method_int_value(method, key, default)
        return value if value > 0 else default

    def set_param(self, key: str, value: int) -> None:
        self.params[key] = value
