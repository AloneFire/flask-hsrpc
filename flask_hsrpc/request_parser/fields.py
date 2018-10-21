# -*- coding: utf-8 -*-
from marshmallow.fields import *
from marshmallow.exceptions import ValidationError
from marshmallow.fields import List as BaseList, Number as BaseNumber
from marshmallow import utils
import enum
from datetime import datetime


class Enum(Field):
    def __type_name__(self):
        enum_item = [f"{str(v.value)} <{k}>" for k, v in self.enum_obj.__members__.items()]
        return f'Enum({" , ".join(enum_item)})'

    def __init__(self, enum_obj, **kwargs):
        super().__init__(**kwargs)
        if issubclass(enum_obj, enum.Enum):
            self.enum_obj = enum_obj
        else:
            raise ValueError("The type is not Enum")

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return value.value

    def _deserialize(self, value, attr, data):
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
    def __type_name__(self):
        field = self.container
        return f'List({field.__type_name__() if hasattr(field, "__type_name__") else field.__class__.__name__})'

    def _deserialize(self, value, attr, data):
        if not utils.is_collection(value):
            value = dict(data).get(attr)
            if not utils.is_collection(value):
                try:
                    result = self.container.deserialize(value)
                    return [result]
                except ValidationError:
                    self.fail('invalid')

        result = []
        errors = {}
        for idx, each in enumerate(value):
            try:
                result.append(self.container.deserialize(each))
            except ValidationError as e:
                result.append(e.data)
                errors.update({idx: e.messages})

        if errors:
            raise ValidationError(errors, data=result)

        return result


class Number(BaseNumber):
    def _deserialize(self, value, attr, data):
        if not self.required and (value is None or value == ''):
            return self.missing
        return self._validated(value)


class DateTime(Field):
    def __type_name__(self):
        return f'DateTime(\"{self.date_format}\")'

    def __init__(self, date_format="%Y-%m-%d %H:%M:%S", **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format

    def _deserialize(self, value, attr, data):
        if not self.required and (value is None or value == ''):
            return self.missing

        local_datetime = datetime.strptime(value, self.date_format)
        return local_datetime
