# -*- coding: utf-8 -*-
from flask import request
from marshmallow import Schema, ValidationError
from ..response import ErrorResponse
from . import validators
from . import fields


class ArgsDict(dict):
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]


class BaseSchema(Schema):
    def get_args(self):
        method = request.method.upper()
        content_type = request.content_type.lower() if request.content_type else None

        if content_type and "x-www-form-urlencoded" in content_type:
            args = request.args
        elif content_type and "json" in content_type:
            args = request.json
        elif method == "POST" or method == "PUT":
            args = request.form
        else:
            args = request.args
        try:
            rel = self.load(args, unknown="INCLUDE")
        except ValidationError as err:
            raise ErrorResponse("args error", "请求参数错误", error_detail=err.args)
        except Exception as err:
            raise ErrorResponse("args error", "请求参数内部错误", error_detail=str(err))
        return ArgsDict(rel)


class PaginationSchema(BaseSchema):
    offset = fields.Integer(missing=0)
    limit = fields.Integer(missing=20)
