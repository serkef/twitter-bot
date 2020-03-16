""" Utilities module containing helper functions """
import logging

from bot.config import DB_SESSION_MAKER


def create_table(query):
    """ Gets a new session and executes provided DDL """

    cursor = DB_SESSION_MAKER()
    cursor.execute(query)
    cursor.commit()
    cursor.close()


def set_logging(loglevel: [int, str] = "INFO"):
    """ Sets logging handlers """

    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
    logging.getLogger("googleapiclient.discovery").setLevel(logging.ERROR)
    logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(loglevel)

    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.setLevel(loglevel)
