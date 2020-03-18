""" Main configuration and settings """

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())

# Script config
RESOURCES = Path(__file__).parent / "resources"
SQL = Path(__file__).parent / "sql"
LOGLEVEL = os.getenv("LOGLEVEL", "INFO")

# Twitter
TWITTER_CONSUMER_KEY = os.environ["CONSUMER_KEY"]
TWITTER_CONSUMER_KEY_SECRET = os.environ["CONSUMER_KEY_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
TWITTER_ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def read_file(filepath):
    """ Opens a file and returns its content as one string """

    with open(filepath, "r") as fin:
        return fin.read()


# Database
DB_CREATE_POSTS_TABLE = read_file(SQL / "post_breaking_data.sql")
DB_GET_BREAKING_UPDATES = read_file(SQL / "query_breaking_data.sql")
DB_INSERT_POST_DATA = read_file(SQL / "insert_post_data.sql")
DB_MIGRATE_DDL = [DB_CREATE_POSTS_TABLE]

# Post settings
STATUS_HEADER = "#BREAKING latest #COVIDー19 #CoronavirusPandemic update"
STATUS_FOOTER = "Visit 📊covid2019app.live for the latest updates"
POST_TWITTER = os.getenv("POST_TWITTER", "false") == "true"
POST_SLACK = os.getenv("POST_SLACK", "false") == "true"
MAX_POST_BATCH_SIZE = int(os.getenv("MAX_POST_BATCH_SIZE", "10"))


def build_db_session_maker():
    """ Creates an sqlalchemy session for db"""

    # db setup
    connection_string = "postgresql://{user}:{psw}@{host}/{db}".format(
        host=os.getenv("DB_HOST", ""),
        db=os.getenv("DB_NAME", ""),
        user=os.getenv("DB_USER", ""),
        psw=os.getenv("DB_PASSWORD", ""),
    )
    engine = create_engine(connection_string, pool_pre_ping=True)
    session = sessionmaker()
    session.configure(bind=engine)
    return session


DB_SESSION_MAKER = build_db_session_maker()

FRIENDLY_NAMES = {
    "Korea, Republic of": "Korea",
    "Korea, republic of": "Korea",
    "United States of America": "U S A",
    "Congo (the Democratic Republic of the)": "Congo",
    "United Kingdom": "U K",
    "United Arab Emirates": "U A E",
}
