# -*- coding: utf-8 -*-
class SwaggerGenerator(object):
    def __init__(self, app, title="", version="", description=""):
        self.app = app
        self.desc = {
            "swagger": "2.0",
            "info": {
                "title": title if title else app.config.get("APP_NAME", "API") if app else "API",
                "description": description if description else app.config.get("APP_DESC", "") if app else "",
                "version": version if version else app.config.get("APP_VERSION", "1.0.0") if app else "1.0.0"
            },
            "paths": {}
        }

    def init(self, app, title="", version="", description=""):
        self.app = app
        self.desc["info"].update({
            "title": title if title else app.config.get("APP_NAME", "API") if app else "API",
            "version": version if version else app.config.get("APP_VERSION", "1.0.0") if app else "1.0.0",
            "description": description if description else app.config.get("APP_DESC", "") if app else ""
        })

    def add_path(self, path, schema=None, methods=None, description="", tags=[]):
        methods = methods if methods else ["GET"]
        path_desc = {}
        for method in methods:
            path_desc[method.lower()] = {
                "summary": description,
                "description": description,
                "tags": tags,
                "parameters": [{
                    "name": field.load_from if field.load_from else key,
                    "type": field.__type_name__() if hasattr(field, "__type_name__") else field.__class__.__name__,
                    "required": field.required,
                    "in": ["path"] if method in ("GET") else ["json"]
                } for key, field in schema._declared_fields.items()] if schema else []
            }

        if not self.desc["paths"].get(path):
            self.desc["paths"][path] = {}

        self.desc["paths"][path].update(path_desc)

    def to_dict(self):
        return self.desc
