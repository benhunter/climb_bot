# [u/climb_bot on Reddit](https://www.reddit.com/user/climb_bot)
climb_bot posts links to rock climbing routes and areas on [MountainProject.com](https://www.mountainproject.com). climb_bot is monitoring the subreddits [r/climbing](https://www.reddit.com/r/climbing) and [r/test](https://www.reddit.com/r/test). climb_bot searches MountainProject for the closest match and links to it, so partial information can often still give a relevant reply.

If climb_bot can't find a match, it won't post a reply at all. Comments that have not been replied to by climb_bot can be edited and climb_bot will keep attempting to find a link. But once a climb_bot replies, it won't look at that comment again.

### Commands
climb_bot looks for the command 'climb:' or '!climb' in comments. adding the keyword 'area' searches for areas on MountainProject. Examples:
* Climb: The Nose, Yosemite
* climb: The Nose, Yosemite
* !Climb The Nose, Yosemite
* !climb The Nose, Yosemite
* climb: area Yosemite Valley
* !climb area Yosemite Valley

### About the code
climb_bot is written in [Python 3](https://www.python.org/). It requires the [PRAW ](https://praw.readthedocs.io/en/latest/)and [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), and uses a [SQLite3](https://docs.python.org/3/library/sqlite3.html) database to record comments that are replied to. The configuration file for the bot is stored in [JSON](https://docs.python.org/3.6/library/json.html) and loaded by [Config.py](https://github.com/benhunter/climb_bot/blob/master/Config.py). The reddit logic is in [climb_bot.py](https://github.com/benhunter/climb_bot/blob/master/climb_bot.py) and replies generated from MountainProject are parsed in [Route.py](https://github.com/benhunter/climb_bot/blob/master/Route.py) and [Area.py](https://github.com/benhunter/climb_bot/blob/master/Area.py).

