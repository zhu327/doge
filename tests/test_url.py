# coding: utf-8

from doge.common.url import URL


def test_url():
    url = URL("", "", "")
    assert url.get_int_value("a", 1) == 1
    url.set_param("a", -1)
    assert url.get_positive_int_value("a", 3) == 3
    assert url.get_int_value("a", 0) == -1
    url.set_param("m.a", 3)
    assert url.get_method_int_value("m", "a", 5) == 3
    assert url.get_method_int_value("m", "b", 5) == 5
    assert url.get_method_positive_int_value("m", "a", 5) == 3
    assert url.get_method_positive_int_value("m", "b", 5) == 5
