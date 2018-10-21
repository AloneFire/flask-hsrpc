# -*- coding: utf-8 -*-
import functools
from .response import response_factory, ErrorResponse
from werkzeug.exceptions import HTTPException
from flask import current_app


def default_decorator(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            rel = func(*args, **kwargs)
            return make_response(rel)

        except ErrorResponse as ex:
            return response_factory(error=ex)

        except Exception as ex:
            current_app.logger.error(ex)
            print("DEBUG:", current_app.config.get("DEBUG", False))
            if current_app.config.get("DEBUG", False):
                raise ex
            return response_factory(error=ex)

    return decorator


def make_response(rel):
    if isinstance(rel, tuple):
        resp = rel[0]
        error = rel[1]
    elif isinstance(rel, ErrorResponse):
        resp = None
        error = rel
    else:
        resp = rel
        error = None
    if resp is None or isinstance(resp, dict) or isinstance(resp, list) or isinstance(resp, tuple):
        return response_factory(data=resp, error=error)
    else:
        return rel


def default_error(ex):
    if isinstance(ex, HTTPException):
        return response_factory(error=ErrorResponse.convert_by_http(ex))
    else:
        return response_factory(error=ErrorResponse("fail", str(ex)))
