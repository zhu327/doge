# coding: utf-8

import random
from typing import List, Optional, Tuple

from doge.cluster.endpoint import EndPoint
from doge.common.doge import Request
from doge.common.url import URL

MaxSelectArraySize = 3
defaultWeight = 1


class RandomLB(object):
    u"""随机 Load Balance"""

    def __init__(
        self, url: URL, endpoints: List[EndPoint], weight: None = None
    ) -> None:
        self.url = url
        self.endpoints = endpoints
        self.weight = None

    def select(self, request: Request) -> Optional[EndPoint]:
        _, ep = select_one_random(self.endpoints)
        return ep

    def select_list(self, request: Request) -> List[EndPoint]:
        index, ep = select_one_random(self.endpoints)
        if not ep:
            return []
        return select_list_from_index(self.endpoints, index)


class RoundrobinLB(object):
    u"""Roundrobin Load Balance"""

    def __init__(
        self, url: URL, endpoints: List[EndPoint], weight: None = None
    ) -> None:
        self.url = url
        self.endpoints = endpoints
        self.weight = None
        self.index = 0

    def select(self, request: Request) -> Optional[EndPoint]:
        _, ep = self.roundrobin_select()
        return ep

    def select_list(self, request):
        index, ep = self.roundrobin_select()
        if not ep:
            return ep
        return select_list_from_index(self.endpoints, index)

    def roundrobin_select(self,) -> Tuple[int, Optional[EndPoint]]:
        eps = self.endpoints
        if not eps:
            return -1, None

        self.index += 1
        idx = self.index % len(eps)
        if eps[idx].available:
            return idx, eps[idx]

        return select_one_random(self.endpoints)


def select_one_random(eps: List[EndPoint]) -> Tuple[int, Optional[EndPoint]]:
    eps_len = len(eps)
    if eps_len == 0:
        return -1, None

    index = random.randint(0, eps_len - 1)
    if eps[index].available:
        return index, eps[index]

    rd = random.randint(0, eps_len - 1)
    for i in range(eps_len):
        rdi = (rd + i) % eps_len
        if eps[rdi].available:
            return rdi, eps[rdi]

    return -1, None


def select_list_from_index(eps: List[EndPoint], index: int) -> List[EndPoint]:
    if not eps or index < 0:
        return []

    eps_len = len(eps)
    ep_list = []
    for i in range(eps_len):
        idx = (index + i) % eps_len
        if eps[idx].available:
            ep_list.append(eps[idx])
        if len(ep_list) == MaxSelectArraySize:
            break
    return ep_list
