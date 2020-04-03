# Doge


[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/zhu327/doge/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/zhu327/doge.svg?branch=master)](https://travis-ci.org/zhu327/doge)
[![codecov](https://codecov.io/gh/zhu327/doge/branch/master/graph/badge.svg)](https://codecov.io/gh/zhu327/doge)
[![codebeat badge](https://codebeat.co/badges/1624b195-bbf5-43d0-9f9d-d330ca09ab76)](https://codebeat.co/projects/github-com-zhu327-doge-master)

Doge is a Python RPC framework like [Alibaba Dubbo](http://dubbo.io/) and [Weibo Motan](https://github.com/weibocom/motan).

## Features

![doge](https://camo.githubusercontent.com/51ff9a1d5530f269f3074e9172483acf14c73eb8/687474703a2f2f6e2e73696e61696d672e636e2f746563682f7472616e73666f726d2f32303136303531302f4a7458792d66787279686875323338323938372e6a7067)

- 服务治理, 服务注册, 服务发现
- 高可用策略, failover, backupRequestHA
- 负载均衡策略, RandomLB, RoundrobinLB
- 限流策略, gevent Pool
- 功能扩展, Opentracing, Prometheus

## Quick Start

### Installation

```sh
pip install dogerpc
```

你可以在[examples](https://github.com/zhu327/doge/tree/master/examples)找到以下实例

### Doge server

1. 新建server端配置文件

```yml
registry:  # 注册中心
  protocol: etcd  # 注册协议, 支持 etcd 与 direct, 默认 etcd
  host: 127.0.0.1  # 注册中心 host
  port: 2379  # 注册中心 port
  # "address": "127.0.0.1:2379,127.0.0.1:4001",  # 注册中心地址, 如果有etcd集群, 可配置多个node
  ttl: 10  # etcd注册ttl, 用于server的心跳检查, 默认10s
service:
  name: test  # 服务名称
  node: n1  # 节点名称
  host: 127.0.0.1  # 服务暴露ip
  port: 4399  # 服务暴露port
  limitConn: 100  # 服务最大连接数, 可选, 默认不限制
  filters:  # 服务端扩展中间件
    - doge.filter.tracing.TracingServerFilter  # opentracing
    - doge.filter.metrics.MetricsServerFilter  # prometheus
```

2. 定义RPC methods类, 启动服务

```python
# coding: utf-8

from gevent import monkey
monkey.patch_socket()  # 依赖gevent

import logging
logging.basicConfig(level=logging.DEBUG)

from doge.rpc.server import new_server


# 定义rpc方法类
class Sum(object):
    def sum(self, x, y):
        return x + y


if __name__ == '__main__':
    server = new_server('server.yaml')  # 基于配置文件实例化server对象
    server.load(Sum)  # 加载暴露rpc方法类
    server.run()  # 启动服务并注册节点信息到注册中心
```

### Doge client

1. 新建client端配置文件

```yml
registry:  # 注册中心
  protocol: etcd  # 注册协议, 支持 etcd 与 direct, 默认 etcd
  host: 127.0.0.1  # 注册中心 host
  port: 2379  # 注册中心 port
  # "address": "127.0.0.1:2379,127.0.0.1:4001",  # 注册中心地址, 如果有etcd集群, 可配置多个node
  ttl: 10  # etcd注册ttl, 用于server的心跳检查, 默认10s
refer:
  haStrategy: failover  # 高可用策略, 支持 failover backupRequestHA, 默认failover
  loadBalance: RoundrobinLB  # 负载均衡策略, 支持 RandomLB RoundrobinLB, 默认RoundrobinLB
  filters:  # 客户端扩展中间件
    - doge.filter.tracing.TracingClientFilter  # opentracing
    - doge.filter.metrics.MetricsClientFilter  # prometheus
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
    cluster = Cluster('client.yaml')  # 基于配置文件实例化Cluster对象
    client = cluster.get_client("test")  # 获取服务名对应的Client对象
    print(client.call('sum', 1, 2))  # 远程调用服务Sum类下的sum方法
```

### Doge filter

`filter`是Doge提供的自定义中间件扩展机制, 当前提供了`jaeger`链路跟踪与`Prometheus`的metrics, `filter`分为客户端`filter`与服务端`filter`, 具体的实例可以参考`filter`目录下的`tracing.py`

#### Metrics

在使用`Prometheus`监控时, 需要在服务节点上配置环境变量`prometheus_multiproc_dir`用于存储`Gunicorn`启动多进程时的`metrics`数据, 然后在服务节点启动`Prometheus Python Exporter`

<https://gist.github.com/zhu327/56cdb58a21a750fb5ca5ae7ccd3e0112>

如何在多进程下使用`Prometheus`请[参考这里]( https://github.com/prometheus/client_python#multiprocess-mode-gunicorn )

## Doge json gateway

基于Bottle实现的json rpc gateway

<https://gist.github.com/zhu327/24c8262dc40c5de7eeaddbfc572f4215>

## Gunicorn server

创建`app.py`, 沿用example中的配置文件`server.json`

```python
# coding: utf-8

from doge.rpc.server import new_server


# 定义rpc方法类
class Sum(object):
    def sum(self, x, y):
        return x + y


server = new_server('server.yaml')  # 基于配置文件实例化server对象
server.load(Sum)  # 加载暴露rpc方法类
```

创建`configs.py`, 填写的bind必须与`server.yaml`配置的监听端口一致
```python
from doge.gunicorn.configs import *

bind = "127.0.0.1:4399"
```

启动Gunicorn

```shell
gunicorn app:server -c configs.py
```

## Requirements

- [gevent](https://github.com/gevent/gevent)
- [mprpc](https://github.com/studio-ousia/mprpc)
- [python-etcd](https://github.com/jplana/python-etcd)
- [pyformance](https://github.com/omergertel/pyformance)
- [pyyaml](https://github.com/yaml/pyyaml)
- [prometheus_client](https://github.com/prometheus/client_python)
- [jaeger-client](https://github.com/monsterxx03/jaeger-client-python)

## License

Apache License, Version 2.0 
