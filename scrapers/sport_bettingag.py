import requests
import pandas as pd

from datetime import datetime
from utils import make_soup
from utils import safety_net
from base_scraper import OddScraper



class SportsBettingScraper(OddScraper):

    def __init__(self, url):
        super().__init__(url)
        self.paths = {'ncaaf': "sportsbook/football/ncaa"}

    def get_NCAAF_lines():
        path = self.url + self.paths['ncaaf']
        table = self.get_odds_table(path)


    @safety_net
    def _get_odds_table(path):
        r = requets.get(path)
        r.raise_for_status()
        soup = make_soup(r.text)
        return soup.find("table", {"class": "league"})


    def _parse_table_ncaaf(table):
        header = self._get_header(table)
        data = self._get_data(table, header)




    def _get_header(table):
        header = table.find("thead").children
        columns = [col.text for col in header]
        columns[0] = "Date"
        return [col or None for col in columns]

    def _get_data(table):
        events = table.find_all(tbody)
        data = []

    def _parse_for_dates(events):
        times = []
        for event in events:
            if event["class"] = "date expanded":
                date_string = event["id"].replace("NCAA", "")
                continue
            row = event.find("tr", {"class": "firstline"})
            timestamp = row.find("td", {"class": "col_time"}).text
            times.append(datetime.strptime(date_string + timestamp, "%Y%m%d%I:%M %p"))
        return times

    def _parse_for_teams(events):
        team_pairs = []
        for event in events:
            pair = []
            for row in event:
                pair.append(find("td", {"class": "col_teamname"}).text)
            team_pairs.append(tuple(pair))
        return team_pairs

    
