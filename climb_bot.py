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


import json
import logging
import re
import socket
import sys
import time

import praw

from Area import findmparea
from Route import findmproute

lock_socket = None  # UNIX Method for long running tasks https://help.pythonanywhere.com/pages/LongRunningTasks

configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
# configpath = '/home/infiniterecursive/climb_bot/config.json'  # path on linux server

config = None  # store the JSON loaded from config file


def is_bot_running_win32():
    return False


def is_bot_running_UNIX():
    """
    Check if an instance of climb_bot is already running by creating a named socket. If the socket cannot be bound to
    the lock name, then the bot is already running on the system
    :return:
    """
    # Can't do any logging here because we haven't config'd the logger yet.
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)  # AF_UNIX doesn't exist on Windows (ignore warning)
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

    # TODO error handling for file/config load and authentication
    # print('Loading config: ', configpath)
    logging.info('Loading config from: ' + configpath)

    with open(configpath, 'r') as configfile:
        config = json.load(configfile)
    logging.info('Config loaded')

    # print('Authenticating to Reddit...')
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

        if match:  # necessary to check?
            logging.debug('Found match: ' + str(match))
            logging.info('Found command in comment: ' + comment.id + '; ' + match[0][0] + ' ; ' + comment.permalink)
            logging.debug('vars(comment): ' + str(vars(comment)))

            query = match[0][1]
            logging.debug('match[0][1]: ' + match[0][1])

            file_obj_r = open(config['bot.commentpath'], 'r')  # with statement

            if comment.id not in file_obj_r.read().splitlines():
                logging.info('Comment ID is unique: ' + comment.id + ' ...retrieving route info and link')

                # TODO see what command we are executing
                # check for  '!climb area'
                areaMatch = re.findall('[Aa]rea (.*)', query)
                if len(areaMatch) > 0:
                    query = areaMatch[0]
                    logging.info('Found Area command in comment: ' + comment.id)
                    currentArea = findmparea(query)
                else:
                    # check for Route command, otherwise assume we are handling a route.
                    routeMatch = re.findall('[Rr]oute (.*)', query)
                    if len(routeMatch) > 0:
                        query = routeMatch[0]
                        logging.info('Found Route commnd in comment: ' + comment.id)
                    else:
                        logging.info('No additional command found; processing as Route command')

                    # find the MP route link
                    currentRoute = findmproute(query)
                    if currentRoute is not None:
                        logging.info('Posting reply to comment: ' + comment.id)
                        comment.reply(currentRoute.redditstr() + config['bot.footer'])
                        # TODO does PRAW return the comment ID of the reply we just submitted? Log permalink
                        logging.info('Reply posted to comment: ' + comment.id)
                        logging.info('Opening comment file to record comment: ' + comment.id)
                        file_obj_w = open(config['bot.commentpath'], 'a+')  # with statement
                        file_obj_w.write(comment.id + '\n')
                        file_obj_w.close()
                        logging.info('Comment file updated with comment: ' + comment.id)
                    else:
                        logging.warning('ERROR RETRIEVING LINK AND INFO FROM MP. Comment: ' + comment.id +
                                        '. Body: ' + comment.body)
            else:
                logging.info('Already visited comment: ' + comment.id + ' ...no reply needed.')

            file_obj_r.close()


if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            if is_bot_running_win32():
                raise Exception('climb_bot is already running!')
        else:
            if is_bot_running_UNIX():
                raise Exception('climb_bot is already running!')
    except:
        print('climb_bot is already running!')
        print('Exiting...')

        sys.exit(-1)

    reddit = init()

    print('Running climb_bot...')
    logging.info('Running climb_bot...')

    count = 0
    while True:

        for sub in config['bot.subreddits']:
            main(reddit, sub)

        logging.info('Loop count is: ' + str(count))
        count += 1

        logging.info('Sleeping ' + str(config['bot.sleep']) + ' seconds...')
        time.sleep(config['bot.sleep'])
