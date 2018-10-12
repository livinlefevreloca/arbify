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



logging.basicConfig(level="INFO")

class FiveDimesScraper(OddScraper):
    def __init__(self, url, sport, site, sel=True):
        super().__init__(url, sport, site, sel=sel)

    def _get_NCAAF_lines(self):
        self._navigate_to_NCAAF()
        sleep(1)
        markup = self._get_markup_ncaaf()
        return self._parse_markup_ncaaf(markup)

    def _navigate_to_NCAAF(self):
        try:
            self.driver.get(self.url)
            print(self.driver.session_id)
            username = self.driver.find_element_by_id("customerID")
            username.send_keys(os.environ["FIVEDIMES_USER"])
            sleep(randrange(1,3))
            password = self.driver.find_elements_by_class_name("login")[1]
            password.send_keys(os.environ["FIVEDIMES_PW"])
            sleep(randrange(1,3))
            self.driver.find_element_by_id("submit1").click()
            sleep(randrange(2))
            print(self.driver.session_id)
            self.driver.find_element_by_id("Football_College").click()
            sleep(randrange(1,3))
            self.driver.find_element_by_id("btnContinue").click()
        except Exception as e:
            logging.exception(e)
        finally:
            sleep(50)
            self.driver.close()

    def _get_markup_ncaaf(self):
        sleep(randrange(1,3))
        data = self.driver.page_source
        #self.driver.close()
        return make_soup(data.get_attribute("innerHTML")).find_all("table", {"id": "tblFootballCollegeGame"})

    def _parse_markup_ncaaf(self, markup):
        header = self.headers
        content = self._get_data_ncaaf(markup, header)
        return pd.DataFrame(data=content)

    def _get_data_ncaaf(self, markup, header):
        events = self._aggregate_rows(markup)
        cotent = {column: list() for column in header}
        for event in events:
            content["Teams"].append(self._parse_for_teams_ncaaf(event))
            content["Date"].append(self._parse_for_dates_ncaaf(event))
            content["Spread"].append(self._parse_for_spread_ncaaf_spread(event))
            content["Total Points"].append(self._parse_for_OU_ncaaf(event))
            content["Money Line"].append(self._parse_for_moneyline_ncaaf(event))

    def _parse_for_dates_ncaaf(self, event):
        date_str = " ".join((event[0].find_all("td")[0] +"/2018", event[1].find_all("td")[0]))
        return datetime.strptime(date_str, "%a, %m/%d/%Y %I:%M%p")

    def _parse_for_teams_ncaaf(self, event):
        team1 = re.sub(re.compile('[0-9]+ ', "", event[0][2].text))
        team2 = re.sub(re.compile('[0-9]+ ', "", event[1][2].text))
        return (team1, team2)

    def _parse_for_spread_ncaaf(self, event):
        spreads = []
        for item in event:
            select = item[3].find_all("select")
            if select:
                options = [option.text for  option in select[0].find_all("option")]
            else:
                options = [item.text,]
            spreads.append(tuple(options))
        return tuple(spreads)

    def _parse_for_moneyline_ncaaf(event):
        mlines = []
        for item in event:
            mline.append(item.text)
        return tuple(mlines)

    def _parse_for_ou_ncaaf(self, event):
        ous = []
        for item in event:
            select = item[5].find_all("select")
            if select:
                options = [option.text for  option in select[0].find_all("option")]
            else:
                options = [item.text,]
            ous.append(tuple(options))
        return tuple(ous)


    def _aggregate_rows(self, markup):
        top = markup.find_all("tr", {"class": "linesRow"})
        bot = markup.find_all("tr", {"class": "linesRowBot"})
        return tuple(zip(top, bot))
