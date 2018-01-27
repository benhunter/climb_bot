import logging
# import praw
import sys

import climb_bot

# import Config


if sys.platform == 'win32':
    climb_bot.configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
else:
    climb_bot.configpath = './config.json'  # path on linux server, duh it's in the same directory

# config = Config.Config(configpath)
reddit_client = climb_bot.init()
climb_bot.config.reddit_commentsPerCheck = 3
subreddit = "test"

logging.info('Getting ' + str(climb_bot.config.reddit_commentsPerCheck) + ' comments from r/' + subreddit)

for comment in reddit_client.subreddit(subreddit).comments(limit=climb_bot.config.reddit_commentsPerCheck):
    # print(comment, comment.link_permalink)
    print(comment.link_permalink + str(comment) + '/')  # here is how to generate a full link to the comment

# TODO find a comment based only on it's id: dtbkk0a

comment = reddit_client.comment('dtbkk0a')
print(comment, comment.body)
print(dir(comment))
