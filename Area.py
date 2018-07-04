import json
import logging
import re
import unittest
import urllib.parse

import requests
from bs4 import BeautifulSoup


# TODO more logging
class Area:
    """
    Area on MountainProject.com
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
        return '[' + self.name + '](' + self.mpurl + ') (Area on MountainProject.com)\n***\nDescription: ' + self.description


def findmparea(query, logger=logging):
    """
    Find the best match for an area on MountainProject.com based on the provided string.
    :param query: String with the query hopefully containing the name of the area.
    :return: Area object or None if no area was find.
    """

    logger.debug('findmparea( query= ' + query + ')')

    searchlink = 'https://www.mountainproject.com/ajax/public/search/results/overview?q=' + urllib.parse.quote(query)
    logger.debug('searchlink: ' + searchlink)

    name = ''
    link = None

    r = requests.get(searchlink)
    j = json.loads(r.content.decode('utf-8'))
    logger.debug('json loaded')

    if len(j['results']) > 0 and j['results'].get('Areas'):
        ajax = j['results']['Areas'][0]
        soup = BeautifulSoup(ajax, 'html.parser')

        name = soup.tr.td.a.string
        logger.debug('name: ' + name)
        sublink = soup.tr.td.strong.a['href']
        link = 'https://www.mountainproject.com' + sublink

        # Making a new request to the Area's page and parsing out the Description.
        req_area_details = requests.get(link)
        soup_area_details = BeautifulSoup(req_area_details.content, 'html.parser')

        # get the number that MountainProject uses to ID the Area.
        area_id = int(re.compile(r'\/area\/(.*)\/').search(sublink).group(1))

        # use the ID to navigate to the closest <a> tag. The ID in the tag is always 1 more than the Area ID.
        marker = soup_area_details.find(attrs={'name': 'a_' + str(area_id + 1)})

        description = str(marker.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling).strip()

        if description == '' and marker.next_sibling.next_sibling.get_text().strip() == 'Description':
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

    def test_findmparea_simple(self):
        r = findmparea('New River Gorge')
        self.assertEqual(r.mpurl,
                         'https://www.mountainproject.com/area/106040788/new-river-gorge-proper?search=1&type=area&method=resultsPage&query=New%20River%20Gorge')
        self.assertEqual(r.name, 'New River Gorge Proper')

        # TODO fix description parsing?
        # self.assertEqual(None, r.description)
        self.assertEqual(r.description,
                         'This is the quintessential NRG area with varied climbing on all types of features. During the summer there are cooler crags such as Kaymoor, Sunshine, South Nuttal, and sometimes Beauty (depends on wall). The winter brings the cooler temps and crags like Endless that get full sun are prime. Welcome to the NRG.')

    def test_findmparea_complicated(self):
        r = findmparea('Yosemite')
        self.assertEqual(r.mpurl,
                         'https://www.mountainproject.com/area/105833388/yosemite-valley?search=1&type=area&method=resultsPage&query=Yosemite')
        self.assertEqual(r.name, 'Yosemite Valley')
        self.assertEqual(r.description,
                         '[Suggest Change]\nYosemite Valley is THE PLACE for many rock climbers. A literal mecca for climbers across the globe, the crags and walls of "The Valley" see thousands of climber-days in the course of a year. During the height of the season, it\'s typical to hear climbers on El Capitan yelling back and forth in English, German, Japanese, Russian and many other languages. In this one place, many factors come together to form a nearly perfect arena for rock climbing; mild weather, beautiful scenery, and incredible granite walls perfectly suited to climbing. On a rest day, visit the many tremendous waterfalls, hike some of the beautiful trails, and breathe in one of the most incredible places in the entire country.')


if __name__ == '__main__':
    unittest.main()
