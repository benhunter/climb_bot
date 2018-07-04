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
        link = 'https://www.mountainproject.com' + sublink  # TODO remove characters after '?'

        # Making a new request to the Area's page and parsing out the Description.
        req_area_details = requests.get(link)
        soup_area_details = BeautifulSoup(req_area_details.content, 'html.parser')

        # get the number that MountainProject uses to ID the Area.
        area_id = int(re.compile(r'\/area\/(.*)\/').search(sublink).group(1))

        # use the ID to navigate to the closest <a> tag. The ID in the tag is (almost) always 1 more than the Area ID
        marker = soup_area_details.find(attrs={'name': 'a_' + str(area_id + 1)})
        if not marker:
            marker = soup_area_details.find(attrs={'name': 'a_' + str(area_id + 2)})

        description_tag = marker.parent.find(class_='fr-view')

        if not description_tag:
            description_tag = marker.parent.parent.find(class_='fr-view')

        description = description_tag.string
        if not description:
            description = description_tag.next_element.string

        # TODO fix error here. Syntax may have changed?
        # description = str(marker.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling).strip()
        # description = str(marker.next_sibling.next_sibling.next_sibling.next_sibling.contents[4].contents[0]).strip()
        # tag_climbareapage = soup_area_details.find(id='climb-area-page')
        # description = tag_climbareapage.find(class_='fr-view').string

        # Or: find a tag h2 with 'Description'.strip() in the tag content (ignore url, <a> tag)?

        # if description == '' and marker.next_sibling.next_sibling.get_text().strip() == 'Description':
        #     description = soup_area_details.select('#text-2')[0].get_text().strip()

        return Area(mpurl=link, name=str(name), description=str(description))

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
        self.assertEqual(
            'https://www.mountainproject.com/area/106040788/new-river-gorge-proper?search=1&type=area&method=resultsPage&query=New%20River%20Gorge',
            r.mpurl)
        self.assertEqual('New River Gorge Proper', r.name)

        # TODO fix description parsing?
        # self.assertEqual(None, r.description)
        self.assertEqual(
            'This is the quintessential NRG area with varied climbing on all types of features. During the summer there are cooler crags such as Kaymoor, Sunshine, and sometimes Beauty (depends on wall). The winter brings the cooler temps and crags like Endless that get full sun are prime. Welcome to the NRG. \xa0Be aware that if you are bringing a dog to the crag within the New River Gorge, it\'s on National Park Service land, and thus you\'ll need to keep dogs a leash.',
            r.description)

    def test_findmparea_complicated(self):
        r = findmparea('Yosemite')
        self.assertEqual(
            'https://www.mountainproject.com/area/105833388/yosemite-valley?search=1&type=area&method=resultsPage&query=Yosemite',
            r.mpurl)
        self.assertEqual('Yosemite Valley', r.name)
        # self.assertEqual('Yosemite Valley is THE PLACE for many rock climbers. A literal mecca for climbers across the globe, the crags and walls of "The Valley" see thousands of climber-days in the course of a year. During the height of the season, it\'s typical to hear climbers on El Capitan yelling back and forth in English, German, Japanese, Russian and many other languages. In this one place, many factors come together to form a nearly perfect arena for rock climbing; mild weather, beautiful scenery, and incredible granite walls perfectly suited to climbing. On a rest day, visit the many tremendous waterfalls, hike some of the beautiful trails, and breathe in one of the most incredible places in the entire country.', r.description[:20])
        self.assertEqual(
            'Yosemite Valley is THE PLACE for many rock climbers. A literal mecca for climbers across the globe, the crags and walls of "The Valley" see thousands of climber-days in the course of a year. During the height of the season, it' + "'" + 's typical to hear climbers on El Capitan yelling back',
            r.description[:280])
        # self.assertEqual(r.description, r.description)
        # d = r.description

    def test_failed(self):
        r = findmparea('Acéphale')
        self.assertEqual(
            'https://www.mountainproject.com/area/113505724/acephale?search=1&type=area&method=resultsPage&query=Ac%C3%A9phale',
            r.mpurl)
        self.assertEqual('Acéphale', r.name)
        self.assertEqual(
            'Acéphale. Pronounced Ass-Ah-Fail by the locals (Should be more like ah-KAY-Fall-luh) is a premier class on the flanks of Heart Mountain. Blue streaked, blocky, and pavement grey limestone buttresses are tucked away in the quiet trees. You can almost ignore the semis engine braking their way into Canmore.',
            r.description)


if __name__ == '__main__':
    unittest.main()
