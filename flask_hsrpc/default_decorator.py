# -*- coding: utf-8 -*-
import functools
from .response import response_factory, ErrorResponse
from werkzeug.exceptions import HTTPException
from flask import current_app
import traceback


def default_decorator(func, app):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            rel = func(*args, **kwargs)
            return make_response(rel, default_headers=app.default_headers)

        except ErrorResponse as ex:
            return response_factory(error=ex, headers=app.default_headers)

        except Exception as ex:
            current_app.logger.error(f"{ex}\n{traceback.format_exc()}", extra={'realFunc': func})
            if current_app.config.get("DEBUG", False):
                raise ex
            return response_factory(error=ex, headers=app.default_headers)

    return decorator


def make_response(rel, default_headers=None):
    if isinstance(rel, tuple):
        resp = rel[0]
        error = rel[1] if len(rel) > 1 else None
        headers = rel[2] if len(rel) > 2 else default_headers
    elif isinstance(rel, ErrorResponse):
        resp = None
        error = rel
        headers = default_headers
    else:
        resp = rel
        error = None
        headers = default_headers

    if resp is None or isinstance(resp, dict) or isinstance(resp, list) or isinstance(resp, tuple):
        return response_factory(data=resp, error=error, headers=headers)
    else:
        return rel


def default_error(ex):
    if isinstance(ex, HTTPException):
        return response_factory(error=ErrorResponse.convert_by_http(ex))
    else:
        return response_factory(error=ErrorResponse("fail", str(ex)))
