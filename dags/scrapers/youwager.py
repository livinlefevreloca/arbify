import os
import logging
import re


from random import randrange
from utils import make_soup
from time import sleep
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from scrapers.base_scraper import OddScraper

logging.basicConfig(level="INFO")

ranking_regex = re.compile('\(#\d+\)') #regex to remove rankings in the team names

class YouWagerScraper(OddScraper):

    def __init__(self, sport, sel=True):
        """
        youwager constructor
        :params
            sport(string) -> the sport we want the lines for
            sel(bool) -> whether or not selenium will be used
        """
        site = "youwager"
        super().__init__(sport, site, sel=sel)
        self._ncaaf_odds = None

    def _navigate_to_NCAAF(self):
        """
        navigate the selenium driver to the correct page
        log exception on failure
        """
        try:
            self.driver.get(os.path.join(self.url, self.path))
            self.driver.maximize_window()
            sleep(randrange(1,3))
            sports_ul = self.driver.find_element_by_class_name("side-navbar-nav")
            for li in sports_ul.find_elements_by_tag_name("li"):
                if "Football" in li.get_attribute("innerHTML"):
                    li.find_element_by_tag_name("a").click()
            sleep(1)
            league_ul = self.driver.find_element_by_class_name("leagues-list")
            for li in league_ul.find_elements_by_tag_name("li"):
                if "College" in li.get_attribute("innerHTML"):
                    li.find_element_by_tag_name("a").click()
                    break
        except Exception as e:
            logging.exception(e)

    def _get_markup_ncaaf(self):
        """
        retrieve the html to extract the lines info from

        return(BeautifulSoup object) -> the soup made from the recovered html
        """
        data = self.driver.find_element_by_id("gamesList")
        return make_soup(data.get_attribute("innerHTML"))


    def _get_data_ncaaf(self, markup, header):
        """
        retrieve all the needed data from the html table
        :params
            markup(BeautifulSoup object) -> the full html table
            header(string) -> a list of dictionary keys to use in the return dict

        return(dict) -> a dictionary to be turned into a pandas DataFrame containing the required info
        """
        events = markup.find_all("div", {"class": "game"})
        content = {column: list() for column in header}
        for event in events:
            content["Date"].append(self._parse_for_dates_ncaaf(event))
            content["Teams"].append(self._parse_for_teams_ncaaf(event))
            spread, mline, ou  = self._parse_for_all_lines_ncaaf(event)
            content["Spread"].append(spread)
            content["Money Line"].append(mline)
            content["Total Points"].append(ou)
        return content

    def _parse_for_all_lines_ncaaf(self, event):
        """
        parse for all of the lines within the html
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(tuple) -> a tuple of lines with uncertainity on what is there and not
        """
        rows = event.find_all("div", {"class": "row"})
        team_lines = []
        for row in rows:
            lines = [line.text.strip() for line in row.find_all("label", {"class": "btn-wager-line"})]
            for i in range(3 - len(lines)):
                lines.append("")
            if any(lines):
                team_lines.append(lines)
        lines = tuple(zip(team_lines[0], team_lines[1]))
        return self._parse_lines(lines)

    def _parse_lines(self, lines):
        """
        parse the lines found by _parse_for_all_lines_ncaaf and determine which
        are there and which are not
        :params
            lines(tuple) -> a tuple of unspecified length with uncertainity around
            which lines are there and which are not
        return(tuple) -> a tuple in a specified order with no retrieved value denoted
        by empty strings
        """
        ou = ""
        mline = ""
        spread = ""
        for line in lines:

            if not any(line):
                continue
            elif "O" in line[0] or "U" in line[1]:
                ou = line
            elif len(line[0]) == 4 and len(line[1]) == 4:
                mline = line
            else:
                spread = line
        return (spread, mline, ou)

    def _parse_for_dates_ncaaf(self, event):
        """
        parse for the date of a given game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(datetime) -> a date time obect parsed from the datestring
        """
        date_str = event.find("div", {"class": "date strong"}).find("p").text
        return datetime.strptime(date_str, "%b %a %d, %Y %I:%M %p")

    def _parse_for_teams_ncaaf(self, event):
        """
        parse for the teams of a given game
        :params
            event(BeautifulSoup object) -> a subset of the html table
        return(string) -> a string denoting the teams involved in the event
        """
        return tuple([re.sub(ranking_regex, "", span.text.strip()).strip() for span
                      in event.find_all("span", {"class": "strong"})])
