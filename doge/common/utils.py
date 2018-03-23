# coding: utf-8

import time

from importlib import import_module

from gsocketpool.pool import Pool


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            dotted_path, class_name)
        raise ImportError(msg)


def time_ns():
    s, n = ("%.20f" % time.time()).split('.')
    return int(s) * 1e9 + int(n[:9])


def str_to_host(s):
    h, p = s.split(":")
    return (str(h), int(p))


class ConnPool(Pool):
    def _create_connection(self):
        conn = self._factory(**self._options)
        # conn.open()

        return conn