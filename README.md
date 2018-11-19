# flask-hsrpc (http simple rpc)

[![Build Status](https://travis-ci.com/AloneFire/flask-hsrpc.svg?branch=master)](https://travis-ci.com/AloneFire/flask-hsrpc) ![python](https://img.shields.io/badge/Python-3.6%2B-green.svg)

> 简化接口路由、接口文档、请求参数自动验证、统一响应、日志、服务注册及自动发现等一体化 flask 插件

## 安装

```
pip install flask-hsrpc
# 升级
pip install --upgrade flask-hsrpc
```

## 配置

| 配置项                  | 描述                                    |
| ----------------------- | --------------------------------------- |
| APP_NAME                | 服务名，用于文档展示，及服务注册        |
| APP_VERSION             | 服务版本号，用于文档展示                |
| APP_DESC                | 服务描述，用于文档展示                  |
| SERVICE_INFO            | 服务注册信息                            |
| SERVICE_INFO.service_id | 服务 ID，每个实例唯一(没有则会自动生成) |
| SERVICE_INFO.address    | 服务所在 IP                             |
| SERVICE_INFO.port       | 服务端口                                |
| SERVICE_INFO.check      | 服务健康检查配置                        |
| CONSUL_HOST             | 注册 consul 服务 IP，默认 127.0.0.1     |
| CONSUL_PORT             | 注册 consul 端口，默认 8500             |
| HSRPC_AUTO_UNREGISTER   | 服务停止后自动注销服务                  |
| LOGGER_FORMAT           | 日志格式                                |
| LOGGER_FILENAME         | 日志文件名                              |
| LOGGER_LEVEL            | 日志输出级别                            |
