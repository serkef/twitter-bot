""" Breaking module. Gets latest "breaking" updates and posts to twitter & slack """
import json
import logging

import flag
import pandas as pd
import requests
import tweepy
from country_converter import convert

from bot.config import (
    DB_GET_BREAKING_UPDATES,
    DB_INSERT_POST_DATA,
    DB_MIGRATE_DDL,
    DB_SESSION_MAKER,
    LOGLEVEL,
    MAX_POST_BATCH_SIZE,
    POST_SLACK,
    POST_TWITTER,
    RESOURCES,
    SLACK_WEBHOOK_URL,
    STATUS_FOOTER,
    STATUS_HEADER,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_KEY_SECRET,
)
from bot.utilities import set_logging


def slack_status(status):
    """ Posts a status message to Slack """
    logger = logging.getLogger("bot.breaking:slack_status")
    logger.info(f"Posting status {status!r}")

    if POST_SLACK:
        requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps({"text": status}),
            headers={"Content-Type": "application/json"},
        )
    else:
        logger.info("Will not post to slack - disabled")


def tweet_status(status):
    """ Posts a status message to Twitter """

    logger = logging.getLogger("bot.breaking:tweet_status")
    logger.info(f"Posting status {status!r}")
    media_filepath = RESOURCES / "BREAKING-COVID2019APP.jpg"

    if POST_TWITTER:
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        try:
            api.update_with_media(str(media_filepath), status=status)
        except tweepy.TweepError:
            logger.error(f"Cannot post message {status}", exc_info=True)
    else:
        logger.info("Will not post to twitter - disabled")


def get_hashtag_country(territory):
    """ Gets a hashtag for the country """

    hashword = "".join(c for c in territory.capitalize() if c.isalpha())
    if hashword:
        return f"#{hashword}"
    return territory


def get_emoji_country(territory):
    """ Gets an emoji for the country"""

    try:
        return flag.flag(convert(names=[territory], to="ISO2"))
    except ValueError:
        return ""


def create_status(category, country, value, total):
    """ Creates a status message given Category, Country, Value and Total """

    country = get_hashtag_country(country)
    emoji = get_emoji_country(country)

    cat_word = {
        "case": {"s": "case", "p": "cases"},
        "death": {"s": "death", "p": "deaths"},
    }

    catg_s = cat_word[category]["s"]
    catg_p = cat_word[category]["p"]
    if value == 1:
        msg = (
            f"A new {catg_s} reported today in {emoji}{country}. "
            f"Raises total to {total:,d}."
        )
        if total == 1:
            msg = f"First {catg_s} reported in {emoji}{country}."
    else:
        msg = (
            f"{value:,d} new {catg_p} reported today in {emoji}{country}. "
            f"Raises total to {total:,d}."
        )
        if value == total:
            msg = f"First {value:,d} {catg_s} reported in {emoji}{country}."

    if len(msg) > 240:
        msg = msg.replace("#CoronavirusPandemic ", "")

    status = STATUS_HEADER + "\n\n" + msg + "\n\n" + STATUS_FOOTER
    return status


def main():
    """ main function """

    set_logging(LOGLEVEL)
    logger = logging.getLogger("bot.breaking:main")

    logger.info(f"Migrating db...")
    cursor = DB_SESSION_MAKER()
    for ddl in DB_MIGRATE_DDL:
        cursor.execute(ddl)
    cursor.commit()
    cursor.close()

    logger.info("Getting DB connection")
    db = DB_SESSION_MAKER().bind

    logger.info("Getting latest updates from DB")
    latest = pd.read_sql(DB_GET_BREAKING_UPDATES, con=db)
    if latest.empty:
        logger.info("No new updates.")
        return

    logger.info("Persisting post info to DB")
    db.execute(DB_INSERT_POST_DATA, [(x,) for x in latest.id])

    if len(latest) > MAX_POST_BATCH_SIZE:
        logger.warning("Too many changes. Won't post")
        logger.warning(latest.to_dict())

    for _, rec in latest.iterrows():
        status = create_status(
            rec.rec_category, rec.rec_territory, rec.value, rec.total,
        )
        slack_status(status)
        tweet_status(status)

    logger.info(f"Posted {len(latest)} successfully.")


if __name__ == "__main__":
    main()
