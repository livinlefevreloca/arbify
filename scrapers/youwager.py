import os
import logging
import pandas as pd


from time import sleep
from random import randrange
from utils import make_soup, translate_fraction
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from base_scraper import OddScraper

logging.basicConfig(level="INFO")

class YouWagerScraper(OddScraper):

    def __init__(self, url,  sport, site, sel=True):
        super().__init__(url, sport, sel=sel)

    def _get_NCAAF_lines(self):
        self._navigate_to_ncaaf()
        sleep(1)
        markup = self._get_markup_ncaaf()
        return self._parse_markup_ncaaf(markup)

    def _navigate_to_ncaaf(self):
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
        data = self.driver.find_element_by_id("gamesList")
        self.driver.close()
        return make_soup(data.get_attribute("innerHTML"))


    def _parse_markup_ncaaf(self,markup):
        headers = self.header
        contents = self._get_data_ncaaf(markup, headers)
        return pd.DataFrame(data=contents)

    def _get_data_ncaaf(self, markup, header):
        events = markup.find_all("div", {"class": "game"})
        content = {column: list() for column in header}
        for event in events:
            content["Date"].append(self._parse_for_dates_ncaaf(event))
            content["Teams"].append(self._parse_for_teams_ncaaf(event))
            spread, mline, ou = self._parse_for_all_lines_ncaaf(event)
            content["Spread"].append(spread)
            content["Money Line"].append(mline)
            content["Total Points"].append(ou)
        return content

    def _parse_for_dates_ncaaf(self, event):
        date_str = event.find("div", {"class": "date strong"}).find("p").text
        return datetime.strptime(date_str, "%b %a %d, %Y %I:%M %p")

    def _parse_for_teams_ncaaf(self, event):
        return tuple([span.text.strip() for span
                      in event.find_all("span", {"class": "strong"})])

    def _parse_for_all_lines_ncaaf(self, event):
        rows = event.find_all("div", {"class": "row"})
        team_lines = []
        for row in rows:
            lines = [line.text.strip() for line in row.find_all("label", {"class": "btn-wager-line"})]
            if lines:
                if len(lines) < 3:
                    lines.insert(1, '')
                team_lines.append(lines)

        return tuple(zip(team_lines[0], team_lines[1]))
