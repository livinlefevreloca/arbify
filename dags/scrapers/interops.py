import hashlib
import logging
import os
import re

from utils import make_soup
from time import sleep
from datetime import datetime
from scrapers.base_scraper import OddScraper


ranking_regex = re.compile('\(#\d+\)') #regex to remove rankings in the team names
logging.basicConfig(level="INFO")

class InteropScraper(OddScraper):

    def __init__(self, sport, sel=True):
        """
        interops constructor
        :params
            sport(string) -> the sport we want the lines for
            sel(bool) -> whether or not selenium will be used
        """
        site = "interops"
        super().__init__(sport, site, sel=sel)
        self._ncaaf_odds = None


    def _navigate_to_NCAAF(self):
        """
        navigate the selenium driver to the NCAAF url
        """
        self.driver.get(os.path.join(self.url, self.path))

    def _navigate_to_NBA(self):
        """
        navigate the selenium driver to the NBA url
        """
        self.driver.get(os.path.join(self.url, self.path))


    def _get_markup(self):
        """
        retrieve the html to extract the lines info from

        return(BeautifulSoup object) -> the soup made from the recovered html
        """
        sleep(2)
        data = self.driver.find_element_by_class_name("markettable").get_attribute("innerHTML")
        return make_soup(data)

    def _get_data(self, markup, header):
        """
        retrieve all the needed data from the html table
        :params
            markup(BeautifulSoup object) -> the full html table
            header(string) -> a list of dictionary keys to use in the return dict

        return(dict) -> a dictionary to be turned into a pandas DataFrame containing the required info
        """
        events = markup.find_all("div", {"class": "trw"})
        content = {column: list() for column in header}
        i = 1
        for event in events:
            i +=1
            try:
                odds = event.find_all("div", {"class": "td"})
                content["Teams"].append(self._parse_for_teams(event))
                content["Date"].append(self._parse_for_dates(event))
                content["Spread"].append(self._parse_for_spread(odds[0]))
                content["Total Points"].append(self._parse_for_OU(odds[1]))
                content["Money Line"].append(self._parse_for_moneyline(odds[2]))
            except Exception as e:
                logging.exception(e)
                continue
        return content

    def _parse_for_teams(self, event):
        """
        parse for a set of teams for a single game from a subset of the html
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(string) -> a string denoting the teams involved in the event
        """
        return (re.sub(ranking_regex, "", event.find("div", {"class": "ustop"}).text.strip()).strip(),
                re.sub(ranking_regex, "", event.find("div", {"class": "usbot"}).text.strip()).strip())


    def _parse_for_dates(self, event):
        """
        parse for the date of a game from a subset of the html
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(datetime) -> a datetime object parsed from the date_string built.
        """
        date_string = event.find("span", {"class": "eventdatetime"}).get("title")
        date_string = date_string.replace('<br/>', ' ')
        return datetime.strptime(date_string, "%m/%d/%Y %I:%M %p")


    def _parse_for_spread(self, column):
        """
        parse for the spread of a game from a subset of html
        :params
            column(BeautifulSoup object) -> a subset of the event portion of the html table
        return(tuple) -> tuple of the spreads for a specifed game
        """
        spreads = []
        for item in column.find_all("a"):
            spans = item.find_all("span")
            data = (spans[0].text, spans[1].get("data-o-cnt"))
            spreads.append(" ".join(data))
        return tuple(spreads)


    def _parse_for_OU(self, column):
        """
        parse for the over under of a game from a subset of html
        :params
            column(BeautifulSoup object) -> a subset of the event portion of the html table
        return(tuple) -> a tuple of the over unders for a specifed game
        """
        totals = []
        for item in column.find_all("a"):
            spans = item.find_all("span")
            data = (spans[0].text[0], item.get("data-o-pts"), spans[1].get("data-o-cnt"))
            totals.append(" ".join(data))
        return tuple(totals)


    def _parse_for_moneyline(self, column):
        """
        parse for the moeny line of a game from a subset of html
        :params
            column(BeautifulSoup object) -> a subset of the event portion of the html table
        return(tuple) -> a tuple of the moneylines for a specifed games
        """
        lines = []
        for item in column.find_all("a"):
            lines.append(item.text.strip())
        return tuple(lines)
