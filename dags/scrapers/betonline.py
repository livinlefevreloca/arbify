import time
import hashlib
import logging
import os
import re


from random import randrange
from datetime import datetime
from utils import make_soup
from time import sleep
from scrapers.base_scraper import OddScraper

ranking_regex = re.compile('\(#\d+\)')

class BetOnlineScraper(OddScraper):

    def __init__(self, sport, sel=True):
        """
        bovada constructor
        :params
            sport(string) -> the sport we want the lines for
            sel(bool) -> whether or not selenium will be used
        """
        site = "betonline"
        super().__init__(sport, site, sel=sel)
        self._ncaaf_odds = None


    def _navigate_to_NCAAF(self):
        """
        navigate the selenium driver to the correct url
        """
        self.driver.get(os.path.join(self.url, self.path))
        navs = self.driver.find_elements_by_class_name("topNav")
        for nav in navs:
            if "Football" in nav.get_attribute("innerHTML"):
                if 'expanded' not in nav.find_element_by_tag_name('a').get_attribute('class'):
                    nav.click()
        subnavs = self.driver.find_elements_by_class_name("subNav")

        for nav in subnavs:
            if "NCAA" in nav.get_attribute("innerHTML"):
                nav.find_element_by_tag_name("input").click()
                break
        self.driver.find_element_by_id("viewSelectedId").click()

    def _navigate_to_NBA(self):
        """
        navigate the selenium driver to the correct url
        """
        self.driver.get(os.path.join(self.url, self.path))
        navs = self.driver.find_elements_by_class_name("topNav")
        for nav in navs:
            if "Basketball" in nav.get_attribute("innerHTML"):
                if 'expanded' not in nav.find_element_by_tag_name('a').get_attribute('class'):
                    nav.click()
        subnavs = self.driver.find_elements_by_class_name("subNav")

        for nav in subnavs:
            if "NBA" in nav.get_attribute("innerHTML"):
                nav.find_element_by_tag_name("input").click()
                break
        self.driver.find_element_by_id("viewSelectedId").click()

    def _get_markup(self):
        """
        retrieve the html to extract the lines info from

        return(BeautifulSoup object) -> the soup made from the recovered html
        """
        return make_soup(self.driver.find_element_by_id("contestDetailTable").get_attribute("innerHTML"))



    def _get_data(self, markup, header):
        """
        retrieve the needed data from the markup. moves through the table and
        keeps track of the section it is in to know the date the came takes place
        on
        :params
            markup(BeautifulSoup object) -> the full html table
            header(string) -> a list of dictionary keys to use in the return dict

        return(dict) -> a dictionary to be turned into a pandas DataFrame containing the required info
        """
        events = markup.find_all("tbody")
        content = {column: list() for column in header}
        date_string = ""
        for event in events:
            date = self._parse_for_dates(event, date_string)
            if not isinstance(date, datetime):
                date_string = date
                continue
            else:
                content["Date"].append(date)
            content["Teams"].append(self._parse_for_teams(event))
            content["Spread"].append(self._parse_for_spread(event))
            content["Money Line"].append(self._parse_for_moneyline(event))
            content["Total Points"].append(self._parse_for_OU(event))
        return content

    def _parse_for_dates(self, event, date_str):
        """
        parse for the date of a specfic game. retrieves the time and adds
        it to the current date_str passed in as a param from the parent function
        :params
            event(BeautifulSoup object) -> a subset of the html table
            date_string(string) -> a string to represent the current date determined
            in the parent function
        return(datetime) -> a datetime object parsed from the date_string built.
        """
        if "date" in event["class"]:
            date_string = event["id"].split(" ")[0].replace("NCAA", "").replace('FCS', '')
            return date_string
        row = event.find("tr", {"class": "firstline"})
        timestamp = row.find("td", {"class": "col_time"}).text
        return datetime.strptime(date_str + timestamp, "%Y%m%d%I:%M %p")

    def _parse_for_teams(self, event):
        """
        retreive the teams for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        """
        return tuple(re.sub(ranking_regex, "", team.text.strip()).strip() for team in event.find_all("td", {"class": "col_teamname"}))

    def _parse_for_spread(self, event):
        """
        parse for the spreads for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple containing the spreads for the game
        """
        rows = event.find_all("tr")[:2]
        spreads = []
        for row in rows:
            handicap = row.find_all("td", {"class": "hdcp"})[0]
            price = row.find_all("td", {"class": "odds"})[0]
            spreads.append(" ".join((handicap.text, price.text)))
        return tuple(spreads)

    def _parse_for_moneyline(self, event):
        """
        parse for the money line for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple containing the moneylines for the game
        """
        return tuple(mline.text for mline in event.find_all("td", {"class": "moneylineodds"}))

    def _parse_for_OU(self, event):
        """
        parse for the over unders for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple containing the over unders for the game
        """
        rows = event.find_all("tr")[:2]
        ous = []
        for row in rows:
            ou = row.find_all("td", {"class": "mktdesc"})[0]
            handicap = row.find_all("td", {"class": "hdcp"})[1]
            price = row.find_all("td", {"class": "odds"})[2]
            ous.append(" ".join((ou.text, handicap.text, price.text)))
        return tuple(ous)
