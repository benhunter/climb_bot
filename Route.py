import json
import urllib.parse

import requests
from bs4 import BeautifulSoup


class Route:
    name = ''
    grade = ''
    description = ''
    mpurl = ''

    def __init__(self, name, grade, description, mpurl):
        self.name = name
        self.grade = grade
        self.description = description
        self.mpurl = mpurl

    def __str__(self):
        return ('Route\n\tName: ' + self.name +
                '\n\tGrade: ' + self.grade +
                '\n\tDescription: ' + self.description +
                '\n\tURL: ' + self.mpurl)

    def redditstr(self):
        return ('[' + self.name + ', ' +
                self.grade + ', ' +
                self.description +
                '](' + self.mpurl +
                ') (Route on MountainProject.com)')


def findmproute(query):
    """
    Search MountainProject.com based on the provided string.
    :param query: String with the query hopefully containing name and location of a route.
    :return: Route object or None if no route was found.
    """

    searchlink = 'https://www.mountainproject.com/ajax/public/search/results/overview?q=' + urllib.parse.quote(query)
    # "https://www.mountainproject.com/search?q=" + urllib.parse.quote(query)

    name = ''
    grade = ''
    description = ''
    link = None  # initializing the return variable

    r = requests.get(searchlink)
    j = json.loads(r.content.decode('utf-8'))

    # TODO error handle for no route result (but has area or forum result)

    if len(j['results']) > 0 and j['results'].get('Routes'):
        ajax = j['results']['Routes'][0]
        soup = BeautifulSoup(ajax, 'html.parser')

        name = soup.tr.td.a.string
        grade = soup.find('div', class_='hidden-md-down').strong.string
        description = soup.find('div', class_='hidden-md-down summary').string
        link = 'https://www.mountainproject.com' + soup.tr.td.strong.a['href']

        return Route(name, grade, description, link)

    else:
        return None
