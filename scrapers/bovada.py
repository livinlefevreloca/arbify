import time
import hashlib
import logging
import os
import re
import pandas as pd

from random import randrange
from time import sleep
from datetime import datetime
from utils import make_soup
from base_scraper import OddScraper


class BovadaScraper(OddScraper):

    def __init__(self, url, sport, site, sel=True):
        super().__init__(url, sport, site, sel=sel)

    def _get_NCAAF_lines(self):
        self._navigate_to_NCAAF()
        sleep(1)
        markup = self._get_markup_ncaaf()
        return self._parse_markup_ncaaf(markup)

    def _navigate_to_NCAAF(self):
        self.driver.get(os.path.join(self.url, self.path))

    def _get_markup_ncaaf(self):
        data = self.driver.find_element_by_class_name("grouped-events")
        return make_soup(data.get_attribute("innerHTML"))

    def _parse_markup_ncaaf(self, markup):
        header = self.header
        contents = self._get_data_ncaaf(markup, header)
        return pd.DataFrame(data=contents)

    def _get_data_ncaaf(self, markup, header):
        events = markup.find_all("section", {"class": "coupon content more-info"})
        content = {column: list() for column in header}
        for event in events:
            content["Date"].append(self._parse_for_dates_ncaaf(event))
            content["Teams"].append(self._parse_for_teams_ncaaf(event))
            spread, mline, ou = self._parse_for_all_lines_ncaaf
            content["Spread"].append(self._parse_for_spread_ncaaf(spread))
            content["Money Line"].append(self._parse_for_moneyline_ncaaf(mline))
            content["Total Points"].append(self._parse_for_OU_ncaaf(ou))

        return content

    def _parse_for_dates_ncaaf(self, event):
        span = event.find("span", {"class": "period hidden-xs"})
        t = span.find("time")
        date_str = " ".join((span.text, t.text))
        return datetime.strptime(date_str, "%m/%d/%Y %I:%M%p")

    def _parse_for_teams_ncaaf(self, event):
        anchor = event.find("a", {"class": "game-view-cta"})
        return tuple(team.text for team in anchor.find_all("h4"))

    def _parse_for_all_lines_ncaaf(self, event):
        container = event.find("sp-outcomes", {"class": "markets-container"})
        return tuple(item for item in container.find_all("sp-two-way-vertical", {"class": "market-type)

    def _parse_for_spread_ncaaf(self, line):
        ...
