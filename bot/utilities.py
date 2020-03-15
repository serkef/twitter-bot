""" custom utilities """

import logging
from logging.handlers import TimedRotatingFileHandler

from twitter_bot.config import APP_LOGS


def set_logging(loglevel: [int, str] = "INFO"):
    """ Sets logging handlers """

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(loglevel)

    APP_LOGS.mkdir(parents=True, exist_ok=True)
    log_path = f"{APP_LOGS / 'twitter-monitor.log'}"
    file_handler = TimedRotatingFileHandler(
        filename=log_path, when="midnight", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(loglevel)

    errlog_path = f"{APP_LOGS / 'twitter-monitor.err'}"
    err_file_handler = TimedRotatingFileHandler(
        filename=errlog_path, when="midnight", encoding="utf-8"
    )
    err_file_handler.setFormatter(formatter)
    err_file_handler.setLevel(logging.WARNING)

    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.addHandler(err_file_handler)
    logger.setLevel(loglevel)
