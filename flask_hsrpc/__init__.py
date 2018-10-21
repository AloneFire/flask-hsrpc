# -*- coding: utf-8 -*-
from werkzeug import exceptions

from .default_decorator import default_decorator, default_error
from .swagger import SwaggerGenerator
from .log import init_logger
from .consul import ConsulRegister
from .api_requests import ApiRequests
import atexit


class Hsrpc(object):

    def __init__(self, app=None, prefix="", decorator=default_decorator, catch_error=True):
        """"
        构造函数
        """
        self.prefix = prefix
        self.catch_error = catch_error
        self.decorator = decorator
        self.app = app

        self.functions = {}

        self.swagger = SwaggerGenerator(app)
        self.logger = None
        self.consul = None
        self.apirequests = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        初始化应用
        :param app:
        :return:
        """
        if app:
            self._register_view(app)
            # 注册错误捕获方法
            if self.catch_error:
                app.register_error_handler(exceptions.NotFound, default_error)
                app.register_error_handler(exceptions.MethodNotAllowed, default_error)
                app.register_error_handler(exceptions.InternalServerError, default_error)
                app.register_error_handler(exceptions.BadRequest, default_error)

            self.swagger.init(app)
            init_logger(app)
            self.logger = app.logger
            self.consul = ConsulRegister(app)
            self.apirequests = ApiRequests(self.consul)

            def unregister():
                self.consul.unregister()
                pass

            # 注册注销服务方法
            if app.config.get("HSRPC_AUTO_UNREGISTER", False):
                atexit.register(unregister)

    def register(self, func, func_name=None, model_name=None, use_decorator=True, schema=None, description="",
                 tags=None, **kwargs):
        """
        注册方法
        :param tags:
        :param schema:
        :param description:
        :param use_decorator:
        :param func:
        :param func_name:
        :param model_name:
        :param kwargs:
        :return:
        """

        # 生成路径
        name = func_name if func_name else func.__name__
        if use_decorator and self.decorator:
            view = self.decorator(func)
        else:
            view = func
        if model_name:
            path = self.prefix + "/" + model_name + "/" + name
        else:
            path = self.prefix + "/" + name
        path = path.lower()
        # 生成文档
        api_tags = tags if tags else []
        if model_name:
            api_tags.append(model_name)
        elif not api_tags:
            api_tags.append("Default")

        self.swagger.add_path(path, schema, kwargs.get("methods"), description, api_tags)

        function_info = {
            "func": view,
            "endpoint": model_name + "-" + name if model_name else name,
            "args": kwargs
        }
        self.functions[path] = function_info
        if self.app:
            self.app.add_url_rule(path, endpoint=function_info["endpoint"], view_func=function_info["func"],
                                  **function_info["args"])

    def _register_view(self, app):
        for path, func in self.functions.items():
            app.add_url_rule(path, endpoint=func["endpoint"], view_func=func["func"], **func["args"])

    def route(self, func_name=None, model_name=None, use_decorator=True, schema=None, description="", methods=["POST"],
              tags=None, **options):
        """
        注册路由装饰器
        :param tags:
        :param methods:
        :param use_decorator:
        :param schema:
        :param description:
        :param model_name:
        :param func_name:
        :param use_default_decorator:
        :param options: the options to be forwarded to the underlying
                        :class:`~werkzeug.routing.Rule` object.  A change
                        to Werkzeug is handling of method options.  methods
                        is a list of methods this rule should be limited
                        to (``GET``, ``POST`` etc.).  By default a rule
                        just listens for ``GET`` (and implicitly ``HEAD``).
                        Starting with Flask 0.6, ``OPTIONS`` is implicitly
                        added and handled by the standard request handling.
        """

        def decorator(f):
            options["methods"] = methods if isinstance(methods,list) else [methods]
            self.register(f, func_name, model_name, use_decorator, schema, description, tags, **options)
            return f

        return decorator
