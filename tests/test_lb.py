# coding: utf-8

import random

import pytest

from doge.cluster.lb import RandomLB, RoundrobinLB, MaxSelectArraySize


@pytest.fixture(scope="module")
def eps():
    class C(object):
        pass

    eps = []
    for i in range(10):
        o = C()
        o.available = random.choice([True, False])
        eps.append(o)
    return eps


class TestRandomLB(object):
    lb_class = RandomLB

    def test_select(self, eps):
        lb = self.lb_class(None, eps)
        ep = lb.select(None)
        assert ep.available

    def test_list(self, eps):
        lb = self.lb_class(None, eps)
        eps = lb.select_list(None)
        assert eps
        assert len(eps) <= MaxSelectArraySize
        for ep in eps:
            assert ep.available


class TestRoundrobinLB(TestRandomLB):
    lb_class = RoundrobinLB
