# -*- coding: utf-8 -*-
from requests.api import request
from .response import ErrorResponse


class ApiRequestException(Exception):
    def __init__(self, **kwargs):
        self.code = kwargs.get("code")
        self.message = kwargs.get("message")
        self._request = kwargs.get("_request")
        self.kwargs = kwargs
        super().__init__(f"Hsrpc Api Request Error: {self.code} - {self.message} ({self._request})")


class ApiRequests(object):
    consul = None

    def __init__(self, consul=None, set_default=True):
        if consul:
            self.consul = consul
            if set_default:
                ApiRequests.consul = consul

    def _base_request(self, method, sys_name, func_name, model_name="default", prefix="", protocol="http", **kwargs):
        node = self.consul.get_health_service_node_by_balance(sys_name)
        uri = [prefix if prefix and prefix != "/" else ""]
        if model_name and model_name != "default":
            uri.append(model_name.lower())
        uri.append(func_name)
        if node:
            host = node["Service"]["Address"]
            port = node["Service"]["Port"]
            url = "{protocol}://{host}:{port}{uri}".format(protocol=protocol, host=host, port=port, uri="/".join(uri))
            resp = request(method, url, **kwargs)

            try:
                rel = resp.json()
                error = rel.get("error")
                if error:
                    error["_request"] = f"[{method.upper()}] - {sys_name} - {host}:{port} - {'/'.join(uri)}"
                return rel.get("data"), ApiRequestException(**error)
            except Exception as ex:
                return None, ApiRequestException(**{
                    "code": "request failed",
                    "message": str(ex),
                    "_request": f"[{method.upper()}] - {sys_name} - {host}:{port} - {'/'.join(uri)}"
                })
        else:
            return None, ApiRequestException(**{
                "code": "request failed",
                "message": f"[{sys_name}: not find alive system]",
                "_request": f"[{method.upper()}] - {sys_name} -  - {'/'.join(uri)}"
            })

    def get(self, sys_name, func_name, model_name="default", prefix="", protocol="http", params=None, **kwargs):
        return self._base_request("get", sys_name, func_name, model_name, prefix, protocol, params=params, **kwargs)

    def post(self, sys_name, func_name, model_name="default", prefix="", protocol="http", params=None, **kwargs):
        return self._base_request('post', sys_name, func_name, model_name, prefix, protocol, json=params, **kwargs)

    def put(self, sys_name, func_name, model_name="default", prefix="", protocol="http", params=None, **kwargs):
        return self._base_request('put', sys_name, func_name, model_name, prefix, protocol, json=params, **kwargs)

    def delete(self, sys_name, func_name, model_name="default", prefix="", protocol="http", **kwargs):
        return self._base_request("delete", sys_name, func_name, model_name, prefix, protocol, **kwargs)


def api_get(sys_name, func_name, model_name="default", prefix="", protocol="http", params=None, **kwargs):
    return ApiRequests().get(sys_name, func_name, model_name, prefix, protocol, params, **kwargs)


def api_post(sys_name, func_name, model_name="default", prefix="", protocol="http", params=None, **kwargs):
    return ApiRequests().post(sys_name, func_name, model_name, prefix, protocol, params, **kwargs)


def api_put(sys_name, func_name, model_name="default", prefix="", protocol="http", params=None, **kwargs):
    return ApiRequests().put(sys_name, func_name, model_name, prefix, protocol, params, **kwargs)


def api_delete(sys_name, func_name, model_name="default", prefix="", protocol="http", **kwargs):
    return ApiRequests().delete(sys_name, func_name, model_name, prefix, protocol, **kwargs)
