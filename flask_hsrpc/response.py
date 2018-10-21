# -*- coding: utf-8 -*-
from flask import jsonify
from werkzeug.exceptions import HTTPException


def response_factory(data=None, error=None):
    if error and isinstance(error, ErrorResponse):
        return jsonify({
            "error": {
                "code": error.code,
                "message": error.message,
                "detail": error.detail
            },
            "data": data
        }), error.status_code
    elif error and isinstance(error, Exception):
        return jsonify({
            "error": {
                "code": "error",
                "message": str(error),
                "detail": None
            },
            "data": data
        })
    else:
        return jsonify({
            "error": None,
            "data": data
        }), 200


class ErrorResponse(Exception):
    def __init__(self, code, message="", status_code=400, error_detail=None):
        self.status_code = status_code
        self.message = message
        self.code = code
        self.detail = error_detail

    @staticmethod
    def convert_by_http(ex):
        if isinstance(ex, HTTPException):
            return ErrorResponse(ex.name, ex.description, ex.code)
        return None

    @staticmethod
    def convert_by_dict(err, status_code=400):
        if err:
            return ErrorResponse(code=err.get("code"), message=err.get("message"), error_detail=err.get("detail"),
                                 status_code=status_code)
        return None

    def __str__(self):
        return "ErrorResponse({},{},{}) {}".format(self.code,self.message,self.detail,self.status_code)


def page_response(data, total):
    return {
        "data": data,
        "total": total
    }
