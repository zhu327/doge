# coding: utf-8


class URL(object):
    def __init__(self, host, port, path="", params={}):
        self.host = host
        self.port = port
        self.path = path
        self.params = params

    def get_int(self, key):
        if key in self.params and isinstance(self.params[key], int):
            return self.params[key]
        return None

    def get_int_value(self, key, default):
        value = self.get_int(key)
        return value or default

    def get_positive_int_value(self, key, default):
        value = self.get_int_value(key, default)
        return default if value < 1 else value

    def get_param(self, key, default=None):
        if key in self.params and self.params[key]:
            return self.params[key]
        return default

    def get_method_int_value(self, method, key, default):
        mkey = "".join([method, ".", key])
        value = self.get_int(mkey)
        return value or default

    def get_method_positive_int_value(self, method, key, default):
        value = self.get_method_int_value(method, key, default)
        return value if value > 0 else default

    def set_param(self, key, value):
        self.params[key] = value
