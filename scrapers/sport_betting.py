import requests
import logging
import os
import pandas as pd

from datetime import datetime
from utils import make_soup
from base_scraper import OddScraper



class SportsBettingScraper(OddScraper):

    def __init__(self, url, sport, site, sel=False):
        super().__init__(url, sport, sel=sel)


    def get_NCAAF_lines(self):
        path = os.path.join(self.url, self.path )
        table = self._get_markup_ncaaf_table(path)
        if not table:
            return None
        data = self._parse_markup_ncaaf(table)
        return data


    def _get_markup_ncaaf(self,path):
        try:
            r = requests.get(path)
            r.raise_for_status()
            soup = make_soup(r.text)
            return soup.find("table", {"class": "league"})
        except Exception as e:
            logging.exception(e)
            return None

    def _parse_markup_ncaaf(self, markup):
        header = self.header
        contents = self._get_data_ncaaf(markup, header)
        return pd.DataFrame(data=contents)


    def _get_data_ncaaf(self, markup, header):
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
        if "expanded" in event["class"]:
            print(date_string)
            date_string = event["id"].split(" ")[0].replace("NCAA", "")
            return date_string
        row = event.find("tr", {"class": "firstline"})
        timestamp = row.find("td", {"class": "col_time"}).text
        return datetime.strptime(date_string + timestamp, "%Y%m%d%I:%M %p")



    def _parse_for_teams_ncaaf(self, event):
        pair = []
        for row in event:
            try:
                team = row.find("td", {"class": "col_teamname"}).text
                pair.append(team)
            except Exception as e:
                continue
        return tuple(pair)


    def _parse_for_spread_and_OU_ncaaf(self, event):
        ou = []
        spread = []
        for row in event:
            try:
                scores = row.find_all("td", {"class": "hdcp"})
                lines = row.find_all("td", {"class": "odds"})
                spread.append((scores[0].text, lines[0].text))
                ou.append((scores[1].text, lines[1].text))
            except Exception as e:
                continue
        return tuple(spread), tuple(ou)



    def _parse_for_moneyline_ncaaf(self, event):
        pair = []
        for row in event:
            try:
                pair.append(row.find("td", {"class": "moneylineodds"}).text)
            except Exception as e:
                continue
        return tuple(pair)
