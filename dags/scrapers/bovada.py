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

price_re = re.compile('(\+\d+)|(-\d+)|EVEN') # regex to replace EVEN with 100
ranking_regex = re.compile('\(#\d+\)') # regex to remove ranking from team name


class BovadaScraper(OddScraper):

    def __init__(self, sport, sel=True):
        """
        bovada constructor
        :params
            sport(string) -> the sport we want the lines for
            sel(bool) -> whether or not selenium will be used
        """
        site = "bovada"
        super().__init__(sport, site, sel=sel)
        self._ncaaf_odds = None

    def _navigate_to_NCAAF(self):
        """
        navigate the selenium driver to the ncaaf url
        """
        self.driver.get(os.path.join(self.url, self.path))

    def _navigate_to_NBA(self):
        """
        navigate the selenium driver to the nba url
        """
        self.driver.get(os.path.join(self.url, self.path))

    def _get_markup(self):
        """
        retrieve the html to extract the lines info from

        return(BeautifulSoup object) -> the soup made from the recovered html
        """
        data = self.driver.find_element_by_class_name("grouped-events")
        return make_soup(data.get_attribute("innerHTML"))


    def _get_data(self, markup, header):
        """
        retrieve all the needed data from the html table
        :params
            markup(BeautifulSoup object) -> the full html table
            header(string) -> a list of dictionary keys to use in the return dict

        return(dict) -> a dictionary to be turned into a pandas DataFrame containing the required info
        """
        events = markup.find_all("section", {"class": "more-info"})
        content = {column: list() for column in header}
        for event in events:
            content["Date"].append(self._parse_for_dates(event))
            content["Teams"].append(self._parse_for_teams(event))
            spread, mline, ou = self._parse_for_all_lines(event)
            content["Spread"].append(self._parse_for_spread(spread))
            content["Money Line"].append(self._parse_for_moneyline(mline))
            content["Total Points"].append(self._parse_for_OU(ou))
        return content

    def _parse_for_dates(self, event):
        """
        parse for the date of a game from a subset of the html
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(datetime) -> a datetime object parsed from the date_string built.
        """
        span = event.find("span", {"class": "period hidden-xs"})
        date_str = " ".join(span.text.split())
        if "Q" in date_str:
            return datetime.now()
        return datetime.strptime(date_str, "%m/%d/%y %I:%M %p")

    def _parse_for_teams(self, event):
        """
        parse for a set of teams for a single game from a subset of the html
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(string) -> a string denoting the teams involved in the event
        """
        anchor = event.find("a", {"class": "game-view-cta"})
        return tuple(re.sub(ranking_regex, "", team.text.strip()).strip() for team in anchor.find_all("h4"))

    def _parse_for_all_lines(self, event):
        """
        retrieve the containers for all of the lines we intend to retrieve
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple containg the html containers of all the lines
        """
        container = event.find("sp-outcomes", {"class": "markets-container"})
        return tuple(item for item in container.find_all("sp-two-way-vertical", {"class": "market-type"}))

    def _parse_for_spread(self, line):
        """
        retrieve the spread for a single
        :params
            line(BeautifulSoup object) -> the html to parse the spread out of
        return(tuple) -> a tuple of the spreads for the game
        """
        handicap = [item.text for item in line.find_all("span", {"class": "bet-handicap"})]
        prices = [item.text for item in line.find_all("span", {"class": "bet-price"})]
        price = [re.search(price_re, price).group(0) for price in prices]
        return tuple(" ".join(item) for item in zip(handicap, price))

    def _parse_for_moneyline(self, line):
        """
        retrieve the moneylines for a single
        :params
            line(BeautifulSoup object) -> the html to parse the moneylines out of
        return(tuple) -> a tuple of the moneylines for the game
        """
        prices = [item.text for item in line.find_all("span", {"class": "bet-price"})]
        return tuple(re.search(price_re, price).group(0) for price in prices)

    def _parse_for_OU(self, line):
        """
        retrieve the over under for a single
        :params
            line(BeautifulSoup object) -> the html to parse the over unders out of
        return(tuple) -> a tuple of the over unders for the game
        """
        handicap = [item.text for item in line.find_all("span", {"class": "bet-handicap"})]
        prices = [item.text for item in line.find_all("span", {"class": "bet-price"})]
        handicap = [" ".join((handicap[i], handicap[i+1])) for i in range(0,len(handicap),2)]
        price = price = [re.search(price_re, price).group(0) for price in prices]
        return tuple(" ".join(item) for item in zip(handicap, price))
