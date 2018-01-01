import json
import urllib.parse

import requests
from bs4 import BeautifulSoup


class Area:
    name = ''
    mpurl = ''

    def __init__(self, name, mpurl):
        self.name = name
        self.mpurl = mpurl

    def __str__(self):
        return ('Area Name: ' + self.name +
                '\n\tURL: ' + self.mpurl)

    def redditstr(self):
        return '[' + self.name + '](' + self.mpurl + ') (Area on MountainProject.com)'


def findmparea(query):
    """
    Find the best match for an area on MountainProject.com based on the provided string.
    :param query: String with the query hopefully containing the name of the area.
    :return: Area object or None if no area was find.
    """

    searchlink = 'https://www.mountainproject.com/ajax/public/search/results/overview?q=' + urllib.parse.quote(query)
    name = ''
    link = None

    r = requests.get(searchlink)
    j = json.loads(r.content.decode('utf-8'))

    # TODO error handle for results that don't include Area
    # TODO test the code below
    if len(j['results']) > 0 and j['results'].get('Areas', None) is not None:  # TODO test Areas check
        ajax = j['results']['Areas'][0]
        soup = BeautifulSoup(ajax, 'html.parser')

        name = soup.tr.td.a.string
        link = 'https://www.mountainproject.com' + soup.tr.td.strong.a['href']

        return Area(name, link)
    else:
        return None
