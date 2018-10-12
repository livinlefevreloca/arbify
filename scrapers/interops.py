import time
import hashlib
import logging
import os
import pandas as pd


from utils import make_soup
from datetime import datetime
from base_scraper import OddScraper



logging.basicConfig(level="INFO")

class InteropScraper(OddScraper):

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
        time.sleep(2)
        data = self.driver.find_element_by_class_name("markettable").get_attribute("innerHTML")
        self.driver.close()
        return make_soup(data)


    def _parse_markup_ncaaf(self, markup):
        headers = self.header
        contents = self._get_data_ncaaf(markup, headers)
        return pd.DataFrame(data=contents)

    def _parse_for_teams_ncaaf(self, event):
        return (event.find("div", {"class": "ustop"}).text.strip(),
                event.find("div", {"class": "usbot"}).text.strip())


    def _parse_for_dates_ncaaf(self, event):
        date_string = event.find("span", {"class": "eventdatetime"}).get("title")
        print(date_string)
        date_string = date_string.replace('<br/>', ' ')
        return datetime.strptime(date_string, "%m/%d/%Y %I:%M %p")


    def _parse_for_spread_ncaaf(self, column):
        spreads = []
        for item in column.find_all("a"):
            spans = item.find_all("span")
            data = (spans[0].text, spans[1].get("data-o-cnt"))
            spreads.append(data)
        return tuple(spreads)


    def _parse_for_OU_ncaaf(self, column):
        totals = []
        for item in column.find_all("a"):
            spans = item.find_all("span")
            data = (item.get("data-o-pts"), spans[1].get("data-o-cnt"))
            totals.append(data)
        return tuple(totals)


    def _parse_for_moneyline_ncaaf(self, column):
        lines = []
        for item in column.find_all("a"):
            lines.append(item.text.strip())
        return tuple(lines)

    def _get_data_ncaaf(self, markup, header):
        events = markup.find_all("div", {"class": "trw"})
        content = {column: list() for column in header}
        i = 1
        for event in events:
            i +=1
            try:
                odds = event.find_all("div", {"class": "res2"})
                content["Teams"].append(self._parse_for_teams_ncaaf(event))
                content["Date"].append(self._parse_for_dates_ncaaf(event))
                content["Spread"].append(self._parse_for_spread_ncaaf(odds[0]))
                content["Total Points"].append(self._parse_for_OU_ncaaf(odds[1]))
                content["Money Line"].append(self._parse_for_moneyline_ncaaf(odds[2]))
            except Exception as e:
                logging.exception(e)
                print('\n')
                continue
        print(i)
        for key in content:
            print(key, len(content[key]))
        return content
