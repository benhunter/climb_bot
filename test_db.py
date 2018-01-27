import sqlite3
import sys

import Config
import climb_bot

if sys.platform == 'win32':
    configpath = 'C:/projects/climb_bot/config.json'  # where to find the config JSON
else:
    configpath = './config.json'  # path on linux server, duh it's in the same directory

config = Config.Config(configpath)
# climb_bot.init()


db = sqlite3.connect(config.bot_dbname)
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS comments (comment_id)')
cursor.close()
db.commit()

climb_bot.db = sqlite3.connect(config.bot_dbname)
result = climb_bot.check_already_commented('dsbqb0z')
print(result)
