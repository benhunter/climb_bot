# Simple utility to transfer the list of tracked comments from the file to a database while converting
# the comment tracking capability.

import sqlite3
import sys

import Config

if sys.platform == 'win32':
    configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
else:
    configpath = '/home/infiniterecursive/climb_bot/config.json'  # path on linux server

print(configpath)

config = Config.Config(configpath)

print(config.bot_commentpath)
print(config.bot_dbname)

with open(config.bot_commentpath) as file:
    with sqlite3.connect(config.bot_dbname) as db:
        cursor = db.cursor()
        # cursor.execute('DROP TABLE comments')
        print('Trying: CREATE TABLE IF NOT EXISTS comments (comment_id UNIQUE)')
        cursor.execute('CREATE TABLE IF NOT EXISTS comments (comment_id UNIQUE)')
        for comment in file:
            try:
                comment = comment.strip()
                print('INSERT INTO comments VALUES (?)', (comment,))
                cursor.execute('INSERT INTO comments VALUES (?)', (comment,))
            except sqlite3.IntegrityError as e:
                print('Caught exception', e)
        cursor.close()
        db.commit()
        print('Done updating DB')

with sqlite3.connect(config.bot_dbname) as db:
    cursor = db.cursor()
    data = cursor.execute('SELECT * from comments').fetchall()
    print(data)
    print(len(data))
