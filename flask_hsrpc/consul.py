# -*- coding: utf-8 -*-
from consul import Consul as BaseConsul
from consul.base import CB, Check
from uuid import uuid4 as uuid
import random
import json
import os


def _is_node_health(node):
    checks = node["Checks"]
    return len(list(filter(lambda c: c["Status"] != "passing", checks))) == 0


def random_balance(health_nodes):
    return random.sample(health_nodes, 1)[0]


def _rr_balance_func():
    Next_RR_Balance_Count = 0

    def balance(health_nodes):
        nonlocal Next_RR_Balance_Count
        if Next_RR_Balance_Count >= len(health_nodes):
            Next_RR_Balance_Count = 0
        rel = health_nodes[Next_RR_Balance_Count]
        Next_RR_Balance_Count += 1
        return rel

    return balance


rr_balance = _rr_balance_func()


class Consul(BaseConsul):
    def service_register(
            self,
            name,
            service_id=None,
            address=None,
            port=None,
            tags=None,
            check=None,
            token=None,
            meta=None,
            # *deprecated* use check parameter
            script=None,
            interval=None,
            ttl=None,
            http=None,
            timeout=None,
            enable_tag_override=False,
            connect=None):

        payload = {'name': name}

        if enable_tag_override:
            payload['enabletagoverride'] = enable_tag_override
        if service_id:
            payload['id'] = service_id
        if address:
            payload['address'] = address
        if port:
            payload['port'] = port
        if tags:
            payload['tags'] = tags

        if meta:
            payload['meta'] = meta

        if connect:
            payload['connect'] = connect

        if check:
            payload['check'] = check

        else:
            payload.update(Check._compat(
                script=script,
                interval=interval,
                ttl=ttl,
                http=http,
                timeout=timeout))

        params = {}
        token = token or self.token
        if token:
            params['token'] = token

        return self.http.put(
            CB.bool(),
            '/v1/agent/service/register',
            params=params,
            data=json.dumps(payload))

    def service_deregister(self, service_id):
        return self.http.put(
            CB.bool(), '/v1/agent/service/deregister/%s' % service_id)


class ConsulRegister(object):
    _service_id = ""

    def __init__(self, app):
        host = app.config.get("CONSUL_HOST", "127.0.0.1")
        port = app.config.get("CONSUL_PORT", "8500")
        self.name = app.config.get("APP_NAME")
        self.service_info = app.config.get("SERVICE_INFO")
        self.service_info["service_id"] = self.service_id
        print(self.service_id)
        # self.consul = BaseConsul(host=host, port=port)
        self.consul = Consul(host=host, port=port)

        if self.name:
            print("register service...")
            # self.consul.agent.service.register()
            self.consul.service_register(name=self.name, **self.service_info)

    @property
    def service_id(self):
        if not self._service_id:
            if self.service_info and self.service_info.get("service_id"):
                self._service_id = self.service_info.get("service_id")
            elif os.path.exists("service_id"):
                with open("service_id", "r", encoding="utf-8") as f:
                    self._service_id = f.readline()
            else:
                self._service_id = self.name + '-' + uuid().hex
                with open("service_id", "w", encoding="utf-8") as f:
                    f.write(self._service_id)
        return self._service_id

    def get_service(self, name):
        return self.consul.health.service(name)

    def get_health_service_node_by_balance(self, name, balance=random_balance):
        nodes = self.get_service(name)[1]
        health_nodes = list(filter(lambda n: _is_node_health(n), nodes))
        return balance(health_nodes) if health_nodes else None

    def unregister(self):
        print(self.service_id)
        print("unregister service...")
        self.consul.service_deregister(self.service_id)

# def consul_unregister(app):
#     if app:
#         host = app.config.get("CONSUL_HOST", "127.0.0.1")
#         port = app.config.get("CONSUL_PORT", "8500")
#         name = app.config.get("APP_NAME")
#         service_info = app.config.get("SERVICE_INFO")
#         service_id = service_info.get("service_id") if service_info and service_info.get("service_id") else name
#         consul = Consul(host=host, port=port)
#         print(service_id)
#         print(consul.service_deregister(service_id))
