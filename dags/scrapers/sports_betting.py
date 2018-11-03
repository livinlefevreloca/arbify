import requests
import logging
import os
import re

from datetime import datetime
from utils import make_soup
from scrapers.base_scraper import OddScraper

ranking_regex = re.compile('\(#\d+\)') #regex to remove rankings in the team names


class SportsBettingScraper(OddScraper):

    def __init__(self, sport, sel=True):
        """
        sportsbetting constructor
        :params
            sport(string) -> the sport we want the lines for
            sel(bool) -> whether or not selenium will be used
        """
        site = "sportsbetting"
        super().__init__(sport, site, sel=sel)

    def _navigate_to_NCAAF(self):
        """
        navigate the selenium driver to the correct page
        log exception on failure
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

    def _get_markup_ncaaf(self):
        """
        retrieve the html to extract the lines info from

        return(BeautifulSoup object) -> the soup made from the recovered html
        """
        return make_soup(self.driver.find_element_by_class_name("league").get_attribute("innerHTML"))


    def _get_data_ncaaf(self, markup, header):
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
            date = self._parse_for_dates_ncaaf(event, date_string)
            if not isinstance(date, datetime):
                date_string = date
                continue
            else:
                content["Date"].append(date)

            content["Teams"].append(self._parse_for_teams_ncaaf(event))

            content["Money Line"].append(self._parse_for_moneyline_ncaaf(event))

            spread, ou = self._parse_for_spread_and_OU_ncaaf(event)
            content["Spread"].append(spread)
            content["Total Points"].append(ou)

        return content

    def _parse_for_dates_ncaaf(self, event, date_string):
        """
        parse for the date of a specfic game. retrieves the time and adds
        it to the current date_str passed in as a param from the parent function
        :params
            event(BeautifulSoup object) -> a subset of the html table
            date_string(string) -> a string to represent the current date determined
            in the parent function
        return(datetime) -> a datetime object parsed from the date_string built.
        """
        if "expanded" in event["class"]:
            date_string = event["id"].split(" ")[0].replace("NCAA", "").replace('FCS', '')
            return date_string
        row = event.find("tr", {"class": "firstline"})
        timestamp = row.find("td", {"class": "col_time"}).text
        return datetime.strptime(date_string + timestamp, "%Y%m%d%I:%M %p")



    def _parse_for_teams_ncaaf(self, event):
        """
        retreive the teams for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        """
        pair = []
        for row in event:
            try:
                team = row.find("td", {"class": "col_teamname"}).text
                team = re.sub(ranking_regex, "", team)
                pair.append(team.strip())
            except Exception as e:
                continue
        return tuple(pair)


    def _parse_for_spread_and_OU_ncaaf(self, event):
        """
        parse for both spread and over under for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple of tuples each containing the spreads/OUs for the game
        """
        ou = []
        spread = []
        for row in event:
            try:
                scores = row.find_all("td", {"class": "hdcp"})
                lines = row.find_all("td", {"class": "odds"})
                designation = row.find_all("td", {"class": "mktdesc"})
                spread.append(" ".join((scores[0].text, lines[0].text)))
                ou.append(" ".join((designation[0].text, scores[1].text, lines[1].text)))
            except Exception as e:
                continue
        return tuple(spread), tuple(ou)



    def _parse_for_moneyline_ncaaf(self, event):
        """
        parse for the money line for a single game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple containing the moneylines for the game
        """
        pair = []
        for row in event:
            try:
                pair.append(row.find("td", {"class": "moneylineodds"}).text)
            except Exception as e:
                continue
        return tuple(pair)
