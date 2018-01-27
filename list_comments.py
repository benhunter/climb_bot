# Print links to all the comments in climb_bot's database.

import logging
import sqlite3
import sys

import praw

import Config

if sys.platform == 'win32':
    configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
else:
    configpath = './config.json'  # path on linux

config = Config.Config(configpath)

logging.info('Authenticating to Reddit...')  # TODO don't think it actually auth's yet...
reddit = praw.Reddit(client_id=config.reddit_client_id,
                     client_secret=config.reddit_client_secret,
                     user_agent=config.reddit_user_agent,
                     username=config.reddit_username,
                     password=config.reddit_password)

# TODO verify auth, write rights - how does PRAW do this, can we force auth now?
# When offline, PRAW acts like it already auth'd
if reddit.read_only:
    logging.error('Authentication to Reddit is read-only.')
    raise Exception('Authentication to Reddit is read-only.')
logging.info('Authentication successful.')  # TODO was it really though?

logging.info('Initialization complete.')

db = sqlite3.connect(config.bot_dbname)
cursor = db.cursor()
result = cursor.execute('SELECT comment_id FROM comments')
result = result.fetchall()

for comment in result:
    comment = reddit.comment(comment[0])
    link = comment.link_permalink + str(comment) + '/'
    print(link)
