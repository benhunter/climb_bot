# TODO write test suite
# TODO find way to automatically push code to pythonanywhere.com
# TODO delete own posts if downvoted
# TODO auto-post (instead of being called) route details for a link to mountainproject that someone posted
# TODO email a summary of actions daily
# TODO configure PRAW max retries so program doesn't end when it can't connect
# TODO store list of comment IDs in a database, maybe SQLite

# PythonAnywhere hourly command:
#   workon climb_bot_venv && cd climb_bot/ && python climb_bot.py

# Standard library
import logging
import os
import re
import socket
import sqlite3
import sys
import time

# Reddit API
import praw

# Local imports
from Area import findmparea
from Config import Config
from Route import findmproute

lock_socket = None  # UNIX Method for long running tasks https://help.pythonanywhere.com/pages/LongRunningTasks
config = Config()  # store the Config loaded from JSON config file
db = None

if sys.platform == 'win32':
    configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
    bot_running_file = 'C:/projects/climb_bot/lock.file'
else:
    configpath = '/home/infiniterecursive/climb_bot/config.json'  # path on linux server
    bot_running_file = '/home/infiniterecursive/climb_bot/lock.file'


def stop_bot(delete_lockfile=True, exit_code=0):
    logging.info('Shutting down')
    if delete_lockfile and sys.platform == 'win32' and os.path.isfile(bot_running_file):
        logging.debug('Deleting lock file')
        os.remove(bot_running_file)
    sys.exit(exit_code)


def is_bot_running():
    if sys.platform == 'win32':
        # TODO Using a file for a lock is not working, so we fake it...
        # if os.path.exists(bot_running_file):
        #     os.remove(bot_running_file)
        #     os.open(bot_running_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        #     return True
        # else:
        #     with open(bot_running_file, 'a'):
        #         pass
        return False
    else:
        """
        For UNIX/Linux systems, check if an instance of climb_bot is already running by creating a named socket.
        If the socket cannot be bound to the lock name, then the bot is already running on the system.
        """
        # Can't do any logging here because we haven't config'd the logger yet.
        global lock_socket
        lock_socket = socket.socket(socket.AF_UNIX,
                                    socket.SOCK_DGRAM)  # AF_UNIX doesn't exist on Windows (ignore warning)
        try:
            lock_id = "infiniterecursive.climb_bot"
            lock_socket.bind('\0' + lock_id)
            # logging.debug("Acquired lock %r" % (lock_id,))
            return False
        except socket.error:
            # logging.info("Failed to aquire lock %r" % (lock_id,))
            return True


def record_comment(comment_id):
    """
    Updated the database db with comment_id. Requires global db to be connected already.
    :param comment_id: String with comment ID to add to db.
    """
    cursor = db.cursor()
    logging.info('Database input: INSERT INTO comments VALUES (?)' + comment_id)
    cursor.execute('INSERT INTO comments VALUES (?)', (comment_id,))
    cursor.close()
    db.commit()


def check_already_commented(comment_id):
    """
    Checks the comment database to see if comment_id has already been processed. Requires global db to be
    connected already.
    :param comment_id: String with comment ID to check.
    :return: True if comment ID is in db
    """
    cursor = db.cursor()
    logging.info('Database query: SELECT comment_id FROM comments WHERE comment_id=' + comment_id)
    result = cursor.execute('SELECT comment_id FROM comments WHERE comment_id=?', (comment_id,))
    result = result.fetchall()
    cursor.close()

    if result:
        return True
    else:
        return False
    # return Result?


def init():
    """
    Setup logging.
    Load JSON config.
    Create PRAW Reddit object.
    :return: The configured PRAW Reddit object.
    """

    global config  # JSON config files will be stored here
    global db  # database goes here

    # Configure logging with timestamp and log level. Name the log file by date.
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.DEBUG,
                        filename=time.strftime('%Y_%m_%d') + '.log',
                        filemode='a+')

    logging.info('Initializing...')
    logging.info('Loading config from: ' + configpath)
    config = Config(configpath)
    logging.info('Config loaded')

    logging.info('Loading database: ' + config.bot_dbname)
    db = sqlite3.connect(config.bot_dbname)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS comments (comment_id)')
    cursor.close()
    db.commit()

    # TODO error handling for authentication
    logging.info('Authenticating to Reddit...')  # TODO don't think it actually auth's yet...
    reddit_client = praw.Reddit(client_id=config.reddit_client_id,
                                client_secret=config.reddit_client_secret,
                                user_agent=config.reddit_user_agent,
                                username=config.reddit_username,
                                password=config.reddit_password)

    # TODO verify auth, write rights - how does PRAW do this, can we force auth now?
    # When offline, PRAW acts like it already auth'd
    if reddit_client.read_only:
        logging.error('Authentication to Reddit is read-only.')
        raise Exception('Authentication to Reddit is read-only.')
    logging.info('Authentication successful.')  # TODO was it really though?

    logging.info('Initialization complete.')
    return reddit_client


def main(reddit_client, subreddit):
    """
    Execute the logic of the bot. Run after init() is successful.
    :param reddit_client: PRAW Reddit Object
    :param subreddit: String name of the subreddit to check
    :return: Nothing
    """

    logging.info('Getting ' + str(config.reddit_commentsPerCheck) + ' comments from r/' + subreddit)
    for comment in reddit_client.subreddit(subreddit).comments(limit=config.reddit_commentsPerCheck):
        match = re.findall('(![Cc]limb|[Cc]limb:) (.*)', comment.body)  # gives a list of tuples (two groups in regex)

        if match:
            logging.info('Found command ' + str(match) + ' in comment: ' + comment.id + ' ; ' + comment.permalink)
            query = match[0][1]  # take the first Tuple in the List, and the second regex group from the Tuple

            if not check_already_commented(comment.id):
                logging.info('Comment ID has not been processed yet: ' + comment.id)
                logging.debug('vars(comment): ' + str(vars(comment)))

                # check for  '!climb area'
                area_match = re.findall('[Aa]rea (.*)', query)
                if area_match:
                    query = area_match[0]
                    logging.info('Found Area command in comment: ' + comment.id)
                    logging.debug('Searching MP for Area query: ' + query)
                    current_area = findmparea(query)
                    # TODO implement code to post comment for Area
                else:
                    # check for Route command, otherwise assume we are handling a route.
                    route_match = re.findall('[Rr]oute (.*)', query)
                    if route_match:
                        query = route_match[0]
                        logging.info('Found Route command in comment: ' + comment.id)
                    else:
                        logging.info('No additional command found; processing as Route command')

                    # find the MP route link
                    logging.debug('Searching MP for Route query: ' + query)
                    current_route = findmproute(query)
                    if current_route:
                        logging.info('Posting reply to comment: ' + comment.id)
                        comment.reply(current_route.redditstr() + config.bot_footer)
                        # TODO does PRAW return the comment ID of the reply we just submitted? Log permalink
                        logging.info('Reply posted to comment: ' + comment.id)
                        record_comment(comment.id)
                    else:
                        logging.error('ERROR RETRIEVING LINK AND INFO FROM MP. Comment: ' + comment.id +
                                      '. Body: ' + comment.body)
            else:
                logging.info('Already visited comment: ' + comment.id + ' ...no reply needed.')


if __name__ == '__main__':
    try:
        if is_bot_running():
            raise Exception('climb_bot is already running!')
    except:  # TODO fix bare except statement
        print('climb_bot is already running!')
        print('Exiting...')
        stop_bot(delete_lockfile=True, exit_code=-1)

    reddit = init()

    print('Running climb_bot...')
    logging.info('Running climb_bot...')

    count = 0
    while True:
        for sub in config.bot_subreddits:
            main(reddit, sub)

        count += 1
        logging.info('Loop count is: ' + str(count) + '. Sleeping ' + str(config.bot_sleep) + ' seconds...')
        time.sleep(config.bot_sleep)
