import json
import unittest
import urllib.parse

import requests
from bs4 import BeautifulSoup


class Area:
    """

    """
    mpurl = ''
    name = ''
    description = ''

    def __init__(self, mpurl='', name='', description=''):
        self.mpurl = mpurl
        self.name = name
        self.description = description

    def __str__(self):
        return ('Area Name: ' + self.name +
                '\n\tURL: ' + self.mpurl +
                '\n\tDescription: ' + self.description)

    def redditstr(self):
        return '[' + self.name + '. ' + self.description + '](' + self.mpurl + ') (Area on MountainProject.com)'


# TODO add description from MP
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

    if len(j['results']) > 0 and j['results'].get('Areas'):
        ajax = j['results']['Areas'][0]
        soup = BeautifulSoup(ajax, 'html.parser')

        name = soup.tr.td.a.string
        link = 'https://www.mountainproject.com' + soup.tr.td.strong.a['href']

        # Making a new request to the Area's page and parsing out the Description.
        req_area_details = requests.get(link)
        soup_area_details = BeautifulSoup(req_area_details.content, 'html.parser')
        description = soup_area_details.select('#text-2')[0].get_text().strip()

        return Area(mpurl=link, name=name, description=description)

    else:
        return None


class TestArea(unittest.TestCase):

    def test_init(self):
        r = Area()
        self.assertEqual(r.mpurl, '')
        self.assertEqual(r.name, '')
        self.assertEqual(r.description, '')

    def test_findmparea(self):
        r = findmparea('Yosemite')
        self.assertEqual(r.mpurl,
                         'https://www.mountainproject.com/area/105833388/yosemite-valley?search=1&type=area&method=resultsPage&query=Yosemite')
        self.assertEqual(r.name, 'Yosemite Valley')
        self.assertEqual(r.description,
                         "Yosemite Valley is THE PLACE for many rock climbers. A literal mecca for climbers across the globe, the crags and walls of \"The Valley\" see thousands of climber-days in the course of a year. During the height of the season, it's typical to hear climbers on El Capitan yelling back and forth in English, German, Japanese, Russian and many other languages. In this one place, many factors come together to form a nearly perfect arena for rock climbing; mild weather, beautiful scenery, and incredible granite walls perfectly suited to climbing. On a rest day, visit the many tremendous waterfalls, hike some of the beautiful trails, and breathe in one of the most incredible places in the entire country.")


if __name__ == '__main__':
    unittest.main()
