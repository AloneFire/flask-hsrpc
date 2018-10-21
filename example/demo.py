# -*- coding: utf-8 -*-
from flask import Flask, jsonify, make_response

from flask_hsrpc import Hsrpc
from flask_hsrpc.request_parser import BaseSchema, fields
from flask_hsrpc.response import ErrorResponse
from flask_hsrpc.__version__ import __version__ as hsrpc_version


class Config(object):
    APP_NAME = "Demo"
    APP_VERSION = "0.1.0"
    APP_DESC = "Hsrpc Demo"
    SERVICE_INFO = {
        "address": "192.168.1.6",
        "port": 5301,
        "meta": {
            "apidoc": "/apidocs"
        },
        "check": {
            "name": "health",
            "http": "http://192.168.1.6:5301/health",
            "interval": "5s"
        }

    }
    HSRPC_AUTO_UNREGISTER = True
    CONSUL_HOST = "192.168.1.10"


app = Flask(__name__)
app.config.from_object(Config)
rpc = Hsrpc(app)


class LoginSchema(BaseSchema):
    login_name = fields.String(required=True, load_from="loginName")
    password = fields.String(required=True)


@rpc.route(description="Login Demo", schema=LoginSchema)
def login_demo():
    args = LoginSchema().get_args()
    if args.password == "123456":
        return {
            "welcome": args.login_name
        }
    else:
        raise ErrorResponse("password error", "密码验证失败", status_code=401)


@rpc.route(description="Log Demo")
def log_demo():
    rpc.logger.info("I am write log to file")
    return {
        "status": "ok"
    }


@rpc.route(description="Request Demo")
def request_demo():
    rel, err = rpc.apirequests.post("Demo", "log_demo")
    # or use api_post
    # from flask_hsrpc.api_requests import api_post
    # rel, err = api_post("Demo", "log_demo")
    return rel, err


@rpc.route(methods=["GET", "POST"], description="Hello World")
def hello_world():
    return {
        "hello": "world"
    }


@rpc.route(methods=["GET"], description="Health Check")
def health():
    return {
        "hsrpcVersion": hsrpc_version,
        "status": "ok"
    }


@rpc.route(methods=["GET"], description="swagger api doc json")
def apidocs():
    rst = make_response(jsonify(rpc.swagger.to_dict()))
    rst.headers['Access-Control-Allow-Origin'] = '*'
    rst.headers['Access-Control-Allow-Methods'] = 'GET'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    rst.headers['Access-Control-Allow-Headers'] = allow_headers
    return rst


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5301, debug=True, threaded=True)
