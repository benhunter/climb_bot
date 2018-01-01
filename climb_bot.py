# TODO write test suite
# TODO find way to automatically push code to pythonanywhere.com
# TODO delete own posts if downvoted
# TODO auto-post (instead of being called) route details for a link to mountainproject that someone posted
# TODO email a summary of actions daily
# TODO configure PRAW max retries so program doesn't end when it can't connect
# TODO store list of comment IDs in a database, maybe SQLite
# TODO cleanup the debugging comments because it makes the log file cluttered and hard to read. Simplifiy!

# PythonAnywhere hourly command:
#   workon climb_bot_venv && cd climb_bot/ && python climb_bot.py

# Standard library
import json
import logging
import os
import re
import socket
import sys
import time

# Reddit API
import praw

# Local imports
from Area import findmparea
from Route import findmproute

lock_socket = None  # UNIX Method for long running tasks https://help.pythonanywhere.com/pages/LongRunningTasks
config = None  # store the JSON loaded from config file

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
        if os.path.exists(bot_running_file):
            os.remove(bot_running_file)
            os.open(bot_running_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            return True
        else:
            with open(bot_running_file, 'a'):
                pass
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


def init():
    """
    Setup logging.
    Load JSON config.
    Create PRAW Reddit object.
    :return: The configured PRAW Reddit object.
    """

    global config  # JSON config files will be stored here

    # configure logging with timestamp and log level
    # name the log file by date.
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.DEBUG,
                        filename=time.strftime('%Y_%m_%d') + '.log',
                        filemode='a+')

    logging.info('Initializing...')
    logging.info('Loading config from: ' + configpath)
    with open(configpath, 'r') as configfile:
        config = json.load(configfile)
    logging.info('Config loaded')

    # TODO error handling for authentication
    logging.info('Authenticating to Reddit...')  # TODO don't think it actually auth's yet...
    reddit = praw.Reddit(client_id=config['reddit.client_id'],
                         client_secret=config['reddit.client_secret'],
                         user_agent=config['reddit.user_agent'],
                         username=config['reddit.username'],
                         password=config['reddit.password'])

    # TODO verify auth, write rights - how does PRAW do this, can we force auth now?
    # When offline, PRAW acts like it already auth'd
    if reddit.read_only:
        logging.error('Authentication to Reddit is read-only.')
        raise Exception('Authentication to Reddit is read-only.')
    logging.info('Authentication successful.')  # TODO was it really though?

    logging.info('Initialization complete.')
    return reddit


def main(reddit, subreddit):
    '''
    Execute the logic of the bot. Run after init() is successful.
    :param reddit: PRAW Reddit Object
    :param subreddit: String name of the subreddit to check
    :return: Nothing
    '''
    logging.info('Getting ' + str(config['reddit.commentsPerCheck']) + ' comments from r/' + subreddit)
    for comment in reddit.subreddit(subreddit).comments(limit=config['reddit.commentsPerCheck']):
        match = re.findall('(![Cc]limb|[Cc]limb:) (.*)', comment.body)  # gives a list of tuples (two groups in regex)

        if match:
            logging.info('Found command ' + str(match) + ' in comment: ' + comment.id + ' ; ' + comment.permalink)

            query = match[0][1]  # take the first Tuple in the List, and the second regex group from the Tuple

            file_obj_r = open(config['bot.commentpath'], 'r')  # with statement
            with open(config['bot.commentpath'], 'r') as file_obj_r:
                if comment.id not in file_obj_r.read().splitlines():
                    logging.info('Comment ID is unique: ' + comment.id)
                    logging.debug('vars(comment): ' + str(vars(comment)))

                    # check for  '!climb area'
                    area_match = re.findall('[Aa]rea (.*)', query)
                    if len(area_match) > 0:
                        query = area_match[0]
                        logging.info('Found Area command in comment: ' + comment.id)
                        logging.debug('Searching MP for Area query: ' + query)
                        current_area = findmparea(query)
                        # TODO implement code to post comment for Area
                    else:
                        # check for Route command, otherwise assume we are handling a route.
                        route_match = re.findall('[Rr]oute (.*)', query)
                        if len(route_match) > 0:
                            query = route_match[0]
                            logging.info('Found Route command in comment: ' + comment.id)
                        else:
                            logging.info('No additional command found; processing as Route command')

                        # find the MP route link
                        logging.debug('Searching MP for Route query: ' + query)
                        current_route = findmproute(query)
                        if current_route is not None:
                            logging.info('Posting reply to comment: ' + comment.id)
                            comment.reply(current_route.redditstr() + config['bot.footer'])
                            # TODO does PRAW return the comment ID of the reply we just submitted? Log permalink
                            logging.info('Reply posted to comment: ' + comment.id)
                            logging.info('Opening comment file to record comment: ' + comment.id)

                            # Note that file_obj_r is still open...
                            with open(config['bot.commentpath'], 'a+') as file_obj_w:
                                file_obj_w.write(comment.id + '\n')
                                logging.info('Comment file updated with comment: ' + comment.id)
                        else:
                            logging.warning('ERROR RETRIEVING LINK AND INFO FROM MP. Comment: ' + comment.id +
                                            '. Body: ' + comment.body)
                else:
                    logging.info('Already visited comment: ' + comment.id + ' ...no reply needed.')


if __name__ == '__main__':
    try:
        if is_bot_running():
            raise Exception('climb_bot is already running!')
    except:
        print('climb_bot is already running!')
        print('Exiting...')
        stop_bot(delete_lockfile=True, exit_code=-1)

    reddit = init()

    print('Running climb_bot...')
    logging.info('Running climb_bot...')

    count = 0
    while True:
        for sub in config['bot.subreddits']:
            main(reddit, sub)

        count += 1
        logging.info('Loop count is: ' + str(count) + '. Sleeping ' + str(config['bot.sleep']) + ' seconds...')
        time.sleep(config['bot.sleep'])
