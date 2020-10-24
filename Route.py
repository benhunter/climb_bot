import json
import unittest
import urllib.parse

import requests
from bs4 import BeautifulSoup


class Route:
    """

    """
    mpurl = ''
    name = ''
    grade = ''
    description = ''
    mpsearchurl = ''

    def __init__(self, mpurl='', name='', grade='', description='', mpsearchurl=''):
        self.mpurl = mpurl
        self.name = name
        self.grade = grade
        self.description = description
        self.mpsearchurl = mpsearchurl

    def __str__(self):
        return ('Route\n\tName: ' + self.name
                + '\n\tGrade: ' + self.grade + '\n\tDescription: ' + self.description
                + '\n\tURL: ' + self.mpurl + '\n\tSearch URL: ' + self.mpsearchurl)

    def redditstr(self):
        return ('[' + self.name + ', ' + self.grade + ', ' + self.description + ']('
                + self.mpurl + ') (Route on MountainProject.com)')


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

    if j['results'] and j['results'].get('Routes'):
        ajax = j['results']['Routes'][0]
        soup = BeautifulSoup(ajax, 'html.parser')

        name = soup.tr.td.a.string
        grade = soup.find('div', class_='hidden-md-down').strong.string
        description = soup.find('div', class_='hidden-md-down summary').string
        link = 'https://www.mountainproject.com' + soup.tr.td.strong.a['href']  # TODO remove characters after '?'

        return Route(mpurl=link, name=name, grade=grade, description=description, mpsearchurl=searchlink)

    else:
        return None


class TestRoute(unittest.TestCase):

    def test_init(self):
        r = Route()
        self.assertEqual(r.mpurl, '')
        self.assertEqual(r.name, '')
        self.assertEqual(r.description, '')
        self.assertEqual(r.grade, '')
        self.assertEqual(r.mpsearchurl, '')

    def test_findmproute(self):
        # json.loads = MagicMock(return_value={'results':{'Routes':'data'}})

        r = findmproute('The Nose, Yosemite')

        self.assertEqual(r.mpurl,
                         'https://www.mountainproject.com/route/105924807/the-nose?search=1&type=route&method=resultsPage&query=The%20Nose%2C%20Yosemite')
        self.assertEqual(r.name, 'The Nose')
        self.assertEqual(r.description, 'Trad, Aid, 31 pitches, 3000 ft')
        self.assertEqual(r.grade, '5.9 C2')
        self.assertEqual(r.mpsearchurl,
                         'https://www.mountainproject.com/ajax/public/search/results/overview?q=The%20Nose%2C%20Yosemite')

        self.assertIsNone(findmproute('sdfasdfasfdsfdrandom123'))

    # def test_findmproute_no_network(self):
    #     # json.loads = MagicMock(return_value={'results':'data'})
    #
    #     r = findmproute('The Nose, Yosemite')
    #
    #     self.assertEqual(r.mpurl,
    #                      'https://www.mountainproject.com/route/105924807/the-nose?search=1&type=route&method=resultsPage&query=The%20Nose%2C%20Yosemite')
    #     self.assertEqual(r.name, 'The Nose')
    #     self.assertEqual(r.description, 'Trad, Aid, 31 pitches, 3000 ft')
    #     self.assertEqual(r.grade, '5.9 C2')
    #     self.assertEqual(r.mpsearchurl,
    #                      'https://www.mountainproject.com/ajax/public/search/results/overview?q=The%20Nose%2C%20Yosemite')
    #
    #     self.assertIsNone(findmproute('sdfasdfasfdsfdrandom123'))


if __name__ == '__main__':
    unittest.main()
