# -*- coding: utf-8 -*-
import logging

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


def init_logger(app):

    log_format = app.config.get("LOGGER_FORMAT",
                                "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s")
    log_filename = app.config.get("LOGGER_FILENAME", "app.log")
    log_level = nameToLevel.get(app.config.get("LOGGER_LEVEL", "NOTSET"), logging.INFO)
    handler = logging.FileHandler(log_filename, encoding='UTF-8')
    handler.setLevel(log_level)
    logging_format = logging.Formatter(log_format)
    handler.setFormatter(logging_format)
    app.logger.root.level = log_level
    app.logger.addHandler(handler)
