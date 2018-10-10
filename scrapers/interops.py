import time
import hashlib
import datetime
import logging


from utils import make_soup
from utils import safety_net
from base_scraper import OddScraper



logging.basicConfig(level="INFO")

class InteropScraper(OddScraper):

    def __init__(self, url):
        super().__init__(url)

    def get_NCAAF_lines(self):
        driver = self.driver
        driver.get(self.base_url)
        self.navigate_to_NCAAF()
        raw_html = self.get_all_odds()
        self.driver.close()
        soup = make_soup(raw_html)
        return self.extract_lines(soup)

    def navigate_to_NCAAF(self):
        driver = self.driver
        driver.get("https://sports.intertops.eu/en/Bets/Competition/1016")


    def get_all_odds(self):
        driver = self.driver
        time.sleep(2)
        return driver.find_element_by_id("competition-view-content").get_attribute("innerHTML")

    @safety_net
    def make_event_id(self, team1, team2, event_date):
        date_string = event_date.strftime("%Y-%m-%d")
        full = " ".join((team1, team2, date_string))
        hasher = hashlib.sha224()
        hasher.update(full.encode())
        return hasher.hexdigest()

    @safety_net
    def get_event_team(self, event):
        return (event.find("div", {"class": "ustop"}), event.find("div", {"class": "usbot"}))

    @safety_net
    def get_event_date(self, event):
        date_string = event.find("span", {"class": "eventdatetime"}).get("title")
        date_string = date_string[:date_string.index('<')]
        return datetime.datetime.strptime(date_string, "%m/%d/%Y")

    @safety_net
    def get_spread(self, column):

        spreads = []
        for item in column.find_all("a"):
            spans = item.find_all("span")
            data = (spans[0].text, spans[1].get("data-o-dec"))
            spreads.append(data)
        return tuple(spreads)

    @safety_net
    def get_total(self, column):
        totals = []
        for item in column.find_all("a"):
            spans = item.find_all("span")
            data = (item.get("data-o-pts"), spans[1].get("data-o-dec"))
            totals.append(data)
        return tuple(totals)

    @safety_net
    def get_money_line(self, column):
        lines = []
        for item in column.find_all("a"):
            lines.append(item.get("data-o-inv"))
        return tuple(lines)

    def extract_lines(self, soup, get_total=False):
        events = soup.find_all("div", {"class": "trw"})
        events_dict = {}
        for event in events:
            try:
                names = self.get_event_team(event)
                print(names)
                event_date = self.get_event_date(event)
                print(event_date)
                odds = event.find_all("div", {"class": "res2"})
                print(odds)
                spread = self.get_spread(odds[0])
                print(spread)
                total = self.get_total(odds[1]) if get_total else None
                print(total)
                money_line = self.get_money_line(odds[2])
                print(money_line)
                event_id = self.make_event_id(names[0], names[1], event_date)
                print(event_id)
                events_dict[event_id] = {
                    "team1": {
                                "name": names[0],
                                "spread_pnts": spread[0][0],
                                "spread_odds": spread[0][1],
                                "total_odds": total[0],
                                "money_line": money_line[0]
                             },
                    "team2": {
                                "name": names[1],
                                "spread_pnts": spread[1][0],
                                "spread_odds": spread[1][1],
                                "total_odds": total[1],
                                "money_line": money_line[1]
                             },
                    "date": event_date

                }
            except Exception as e:
                logging.exception(e)
                continue
        return events_dict
