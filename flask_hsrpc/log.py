# -*- coding: utf-8 -*-
import logging
from logging import LogRecord
import inspect
import os

nameToLevel = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


class HsrpcLogFormater(logging.Formatter):
    def format(self, record: LogRecord) -> str:
        real_func_name = record.funcName
        real_file_name = record.filename
        if hasattr(record, "realFunc"):
            pathname = inspect.getmodule(record.realFunc).__file__
            real_file_name = os.path.basename(pathname)
            real_func_name = record.realFunc.__name__
        setattr(record, "realFuncName", real_func_name)
        setattr(record, "realFileName", real_file_name)
        return super().format(record)


def init_logger(app):
    log_format = app.config.get("LOGGER_FORMAT",
                                "%(asctime)s - %(levelname)s - %(realFileName)s - %(realFuncName)s - %(message)s")
    log_filename = app.config.get("LOGGER_FILENAME", "app.log")
    log_level = nameToLevel.get(app.config.get("LOGGER_LEVEL", "NOTSET"), logging.INFO)
    handler = logging.FileHandler(log_filename, encoding='UTF-8')
    handler.setLevel(log_level)
    logging_format = HsrpcLogFormater(log_format)
    handler.setFormatter(logging_format)
    app.logger.root.level = log_level
    app.logger.addHandler(handler)
