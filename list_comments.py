import sqlite3
import sys

import Config

if sys.platform == 'win32':
    configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
else:
    configpath = '/home/infiniterecursive/climb_bot/config.json'  # path on linux server

config = Config.Config(configpath)

db = sqlite3.connect(config.bot_dbname)
cursor = db.cursor()
result = cursor.execute('SELECT comment_id FROM comments')
result = result.fetchall()

print(result)
