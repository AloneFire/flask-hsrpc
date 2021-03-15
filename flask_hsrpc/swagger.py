# -*- coding: utf-8 -*-
import re
from werkzeug.routing import parse_rule
from marshmallow import missing


class SwaggerGenerator(object):
    def __init__(self, app, title="", version="", description=""):
        self.app = app
        host = f"{app.config.get('SERVICE_INFO', {}).get('address', '')}:{app.config.get('SERVICE_INFO', {}).get('port', '')}" if app else ""
        self.doc = {
            "openapi": "3.0.0",
            "info": {
                "title": title if title else app.config.get("APP_NAME", "API") if app else "API",
                "description": description if description else app.config.get("APP_DESC", "") if app else "",
                "version": version if version else app.config.get("APP_VERSION", "1.0.0") if app else "1.0.0"
            },
            "servers": app.config.get("APP_DOC_SERVERS") if app and app.config.get("APP_DOC_SERVERS") else [{
                "url": "http://" + host
            }, {
                "url": '{scheme}://' + host,
                "variables": {
                    "scheme": {
                        "description": "The Data Set API is accessible via https and http",
                        "enum": ["http", "https"],
                        "default": "http"
                    }

                }
            }],
            "paths": {}
        }

    def init(self, app, title="", version="", description=""):
        self.app = app
        self.doc["info"].update({
            "title": title if title else app.config.get("APP_NAME", "API") if app else "API",
            "version": version if version else app.config.get("APP_VERSION", "1.0.0") if app else "1.0.0",
            "description": description if description else app.config.get("APP_DESC", "") if app else ""
        })
        if app and app.config.get("APP_DOC_SERVERS"):
            self.doc["servers"] = app.config.get("APP_DOC_SERVERS")
        else:
            host = f"{app.config.get('SERVICE_INFO', {}).get('address', '')}:{app.config.get('SERVICE_INFO', {}).get('port', '')}" if app else ""
            self.doc["servers"] = [{
                "url": "http://" + host
            }, {
                "url": '{scheme}://' + host,
                "variables": {
                    "scheme": {
                        "description": "The Data Set API is accessible via https and http",
                        "enum": ["http", "https"],
                        "default": "http"
                    }
                }
            }]

    def add_path(self, path, schema=None, methods=None, description="", tags=[]):
        methods = methods if methods else ["GET"]
        path_desc = {}
        for method in methods:
            info = {
                "summary": description,
                "description": description,
                "tags": tags,
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                            }
                        }
                    }
                }
            }
            url_parameters = SwaggerGenerator.extract_path_params(path)
            if url_parameters:
                info["parameters"] = url_parameters
            if schema:
                if method.lower() in ["get"]:
                    if info.get("parameters") is None:
                        info["parameters"] = []
                    info["parameters"] += SwaggerGenerator.parameters_generator(schema._declared_fields)
                else:
                    info["requestBody"] = SwaggerGenerator.request_body_generator(schema._declared_fields)
            path_desc[method.lower()] = info

        RE_URL = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')
        sw_path = RE_URL.sub(r'{\1}', path)

        if not self.doc["paths"].get(sw_path):
            self.doc["paths"][sw_path] = {}

        self.doc["paths"][sw_path].update(path_desc)

    @staticmethod
    def field_schema_convert(field):
        type_str = field.__type_name__() if hasattr(field, "__type_name__") else field.__class__.__name__.lower()
        schema = {
            "type": type_str,
            "description": field.metadata.get("help", "") if field.metadata else "",
        }
        if field.default is not missing or field.missing is not missing:
            schema["default"] = field.default if field.default is not missing else field.missing

        if hasattr(field, "__field_doc_schema__"):
            schema.update(field.__field_doc_schema__())

        return schema

    @staticmethod
    def extract_path_params(path):
        PATH_TYPES = {
            'int': 'integer',
            'float': 'number',
            'string': 'string',
            'default': 'string',
        }
        params = []
        for converter, arguments, variable in parse_rule(path):
            if not converter:
                continue

            if converter in PATH_TYPES:
                url_type = PATH_TYPES[converter]
            else:
                url_type = 'string'

            param = {
                'name': variable,
                'in': 'path',
                'required': True,
                "schema": {
                    "type": url_type
                }
            }

            if converter in PATH_TYPES:
                param['type'] = PATH_TYPES[converter]
            else:
                param['type'] = 'string'
            params.append(param)
        return params

    @staticmethod
    def parameters_generator(declared_fields):
        parameters = []
        for key, field in declared_fields.items():
            desc = field.metadata.get("help", "") if field.metadata else ""
            field_schema = SwaggerGenerator.field_schema_convert(field)
            parameters.append({
                "name": field.data_key if field.data_key else key,
                "description": desc,
                "required": field.required,
                "in": "query",
                "schema": field_schema
            })
        return parameters

    @staticmethod
    def request_body_generator(declared_fields):
        properties = {}
        for key, field in declared_fields.items():
            field_schema = SwaggerGenerator.field_schema_convert(field)
            k = field.data_key if field.data_key else key
            properties[k] = field_schema

        required_list = [field.data_key if field.data_key else key for key, field in declared_fields.items()
                         if field.required]
        request_body = {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": properties
                    }
                }
            }
        }

        if required_list:
            request_body["content"]["application/json"]["schema"]["required"] = required_list

        return request_body

    def to_dict(self):
        return self.doc
