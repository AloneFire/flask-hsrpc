# -*- coding: utf-8 -*-
import enum
from datetime import datetime

from marshmallow.exceptions import ValidationError
from marshmallow.fields import *
from marshmallow.fields import List as BaseList, Number as BaseNumber
from werkzeug.datastructures import ImmutableMultiDict


class Enum(Field):
    def __field_doc_schema__(self):
        enum_values = [e.value for e in self.enum_obj]
        doc = {
            "type": "string",
            "enum": enum_values
        }
        if self.missing or self.default:
            doc["default"] = self.missing.value if self.missing else self.default.value
        return doc

    def __init__(self, enum_obj, **kwargs):
        super().__init__(**kwargs)
        if issubclass(enum_obj, enum.Enum):
            self.enum_obj = enum_obj
        else:
            raise ValueError("The type is not Enum")

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        if not self.required and (value is None or value == ''):
            return self.missing
        try:
            rel_value = value
            if isinstance(rel_value, str):
                if rel_value.isdigit():
                    rel_value = int(rel_value)
            return self.enum_obj(rel_value)
        except ValueError as ex:
            raise ValidationError(str(ex))


class List(BaseList):
    def __field_doc_schema__(self):
        field = self.inner
        sub_schema = field.__field_doc_schema__() if hasattr(field, "__field_doc_schema__") else {
            "type": field.__class__.__name__.lower()
        }
        return {
            "type": "array",
            "items": sub_schema
        }

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(data, ImmutableMultiDict):
            value = data.to_dict(flat=False).get(attr)
        return super()._deserialize(value, attr, data, **kwargs)


class Number(BaseNumber):
    def _deserialize(self, value, attr, data, **kwargs):
        if not self.required and (value is None or value == ''):
            return self.missing
        return self._validated(value)


class DateTime(Field):
    def __field_doc_schema__(self):
        return {
            "type": "string",
            "format": self.date_format
        }

    def __init__(self, date_format="%Y-%m-%d %H:%M:%S", **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format

    def _deserialize(self, value, attr, data, **kwargs):
        if not self.required and (value is None or value == ''):
            return self.missing

        local_datetime = datetime.strptime(value, self.date_format)
        return local_datetime
