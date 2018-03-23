# Doge


[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/zhu327/doge/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/zhu327/doge.svg?branch=master)](https://travis-ci.org/zhu327/doge)
[![codecov](https://codecov.io/gh/zhu327/doge/branch/master/graph/badge.svg)](https://codecov.io/gh/zhu327/doge)

Doge is a Python RPC framework like [Alibaba Dubbo](http://dubbo.io/) and [Weibo Motan](https://github.com/weibocom/motan).

## Features

![doge](https://camo.githubusercontent.com/51ff9a1d5530f269f3074e9172483acf14c73eb8/687474703a2f2f6e2e73696e61696d672e636e2f746563682f7472616e73666f726d2f32303136303531302f4a7458792d66787279686875323338323938372e6a7067)

- 服务治理, 服务注册, 服务发现
- 高可用策略, failover, backupRequestHA
- 负载均衡策略, RandomLB, RoundrobinLB
- 限流策略, gevent Pool

## Quick Start

### Installation

```sh
pip install dogerpc
```

你可以在[examples](https://github.com/zhu327/doge/tree/master/examples)找到以下实例

### Doge server

1. 新建server端配置文件

```javascript
{
    "registry": { // 注册中心
        "protocol": "etcd", // 注册协议, 支持 etcd 与 direct, 默认 etcd
        "host": "127.0.0.1", // 注册中心 host
        "port": 2379, // 注册中心 port
        // "address": "127.0.0.1:2379,127.0.0.1:4001", // 注册中心地址, 如果有etcd集群, 可配置多个node
        "ttl": 10 // etcd注册ttl, 用于server的心跳检查, 默认10s
    },
    "service": {
        "name": "test", // 服务名称
        "node": "n1",　// 节点名称
        "host": "127.0.0.1", // 服务暴露ip
        "port": 4399, // 服务暴露port
        "limitConn": 100 // 服务最大连接数, 可选, 默认不限制
    }
}
```

2. 定义RPC methods类, 启动服务

```python
# coding: utf-8

from gevent import monkey
monkey.patch_socket() # 依赖gevent

import logging
logging.basicConfig(level=logging.DEBUG)

from doge.rpc.server import new_server


# 定义rpc方法类
class Sum(object):
    def sum(self, x, y):
        return x + y


if __name__ == '__main__':
    server = new_server('server.json')  # 基于配置文件实例化server对象
    server.load(Sum)  # 加载暴露rpc方法类
    server.run()  # 启动服务并注册节点信息到注册中心
```

### Doge client

1. 新建client端配置文件

```javascript
{
    "registry": { // 注册中心
        "protocol": "etcd", // 注册协议, 支持 etcd 与 direct, 默认 etcd
        "host": "127.0.0.1", // 注册中心 host
        "port": 2379, // 注册中心 port
        // "address": "127.0.0.1:2379,127.0.0.1:4001", // 注册中心地址, 如果有etcd集群, 可配置多个node
        "ttl": 10 // etcd注册ttl, 用于server的心跳检查, 默认10s
    },
    "refer": {
        "haStrategy": "failover", // 高可用策略, 支持 failover backupRequestHA, 默认failover
        "loadbalance": "RoundrobinLB", // 负载均衡策略, 支持 RandomLB RoundrobinLB, 默认RoundrobinLB
    }
}
```

2. 创建client并call远程方法

```python
# coding: utf-8

from __future__ import print_function

from gevent import monkey
monkey.patch_socket()

import logging
logging.basicConfig(level=logging.DEBUG)

from doge.rpc.client import Cluster

if __name__ == '__main__':
    cluster = Cluster('client.json')  # 基于配置文件实例化Cluster对象
    client = cluster.get_client("test")  # 获取服务名对应的Client对象
    print(client.call('sum', 1, 2))  # 远程调用服务Sum类下的sum方法
```

## doge json gateway

基于Bottle实现的json rpc gateway

<https://gist.github.com/zhu327/24c8262dc40c5de7eeaddbfc572f4215>

## Requirements

- [gevent](https://github.com/gevent/gevent)
- [mprpc](https://github.com/studio-ousia/mprpc)
- [python-etcd](https://github.com/jplana/python-etcd)
- [pyformance](https://github.com/omergertel/pyformance)

## License

Apache License, Version 2.0 