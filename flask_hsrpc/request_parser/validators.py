# -*- coding: utf-8 -*-
from marshmallow.exceptions import ValidationError
import re


class BaseValidator(object):
    def __init__(self, validator=None, error_massage="invalid value"):
        self.error_massage = error_massage
        self.validator = validator

    def __call__(self, value):
        if self.validator and not self.validator(value):
            raise ValidationError(self.error_massage)
        return True


def not_none_and_empty(value):
    if value:
        return True
    else:
        raise ValidationError("value cant be none and empty")


class regex(BaseValidator):
    def __init__(self, regex_str=None, error_massage="invalid value"):
        self.error_massage = error_massage
        self.validator = lambda v: re.match(regex_str, v) is not None


class range(BaseValidator):
    def __init__(self, min=None, max=None):
        self.error_massage = f"the value not in " \
                             f"range ({min if min is not None else ''},{max if max is not None else ''})"
        self.validator = lambda v: not ((min is not None and v < min) or (max is not None and v > max))
