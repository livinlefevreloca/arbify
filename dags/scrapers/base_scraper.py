import logging
import time
import pandas as pd

from selenium import webdriver
from time import sleep


class OddScraper:

    base_urls = {"interops": "https://sports.intertops.eu",
                 "bovada": "https://www.bovada.lv",
                 "betonline": "https://www.betonline.ag",
                 "sportsbetting": "https://www.sportsbetting.ag",
                 "youwager": "https://www.youwager.eu"}

    paths  = {'ncaaf': {"interops": "en/Bets/Competition/1016",
                       "sportsbetting": "sportsbook",
                       "youwager": "sportsbook",
                       "betonline": "sportsbook",
                       "bovada": "sports/football/college-football"
                       },
              'nba': { "youwager": "sportsbook",
                       "sportsbetting": "sportsbook",
                       "interops": "en/Bets/Basketball/NBA-Lines/1070",
                       "bovada": "sports/basketball/nba",
                       "betonline": "sportsbook"
                     },

            }
    headers = {"ncaaf": ("Date", "Teams", "Spread", "Money Line", "Total Points"),
               "nba": ("Date", "Teams", "Spread", "Money Line", "Total Points")}


    def __init__(self, sport, site, sel=False):
        """
        base scraper contstructor hold information about the scraper. All other
        scrapers inherit from this scraper

        :params
            sport(string) -> identify the sport to parsed for
            site(string) -> identify the site to be scraped
            sel(boo) -> is selenium being used
        """
        self.url = OddScraper.base_urls[site]
        self.path = OddScraper.paths[sport][site]
        self.header = OddScraper.headers[sport]
        self.site = site
        self.sel = sel
        self.arbs = []
        self._ncaaf_odds = None
        self._ncaam_odds = None
        self._nba_odds = None

        if sel:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            self.driver = webdriver.Chrome(chrome_options=options)


    @property
    def ncaaf_odds(self):
        """
        ncaaf odds property function. lazily evaluates by calling its setter if
        it is not already set.

        return(unknown) -> the current value of ncaaf_odds
        """
        if self._ncaaf_odds is None:
            logging.warning("ncaaf odds have not be retrieved from {} yet.\
            getting odds now".format(self.site))
            self.set_ncaaf_odds()

        return self._ncaaf_odds

    @property
    def ncaam_odds(self):
        """
        ncaam odds property function. lazily evaluates by calling its setter if
        it is not already set.

        return(unknown) -> the current value of ncaam_odds
        """
        if self._ncaaf_odds is None:
            logging.warning("ncaam odds have not be retrieved from {} yet.\
            getting odds now".format(self.site))
            self.set_ncaam_odds()

        return self._ncaam_odds

    @property
    def nba_odds(self):
        """
        nba odds property function. lazily evaluates by calling its setter if
        it is not already set.

        return(unknown) -> the current value of nba_odds
        """
        if self._nba_odds is None:
            logging.warning("nba odds have not be retrieved from {} yet.\
            getting odds now".format(self.site))
            self.set_nba_odds()

        return self._nba_odds

    def set_ncaaf_odds(self, df=None):
        """
        ncaaf_odds property setter. if a data frame is passed to it sets the
        ncaaf_odds attribute to that df. Otherwise set off the scraping process.
        :params
            df(pandas DataFrame) -> a data frame to set ncaaf_odds to
        """
        if self._ncaaf_odds is not None:
            self._ncaaf_odds = df
        else:
            self._navigate_to_NCAAF()
            sleep(3)
            markup = self._get_markup()
            self._ncaaf_odds = self._parse_markup_ncaaf(markup)

    def set_ncaam_odds(self, df=None):
        """
        ncaam_odds property setter. if a data frame is passed to it sets the
        ncaam_odds attribute to that df. Otherwise set off the scraping process.
        :params
            df(pandas DataFrame) -> a data frame to set ncaam_odds to
        """
        if self._ncaam_odds is not None:
            self._ncaam_odds = df
        else:
            self._navigate_to_NCAAM()
            sleep(3)
            markup = self._get_markup()
            self._ncaam_odds = self._parse_markup_ncaam(markup)

    def set_nba_odds(self, df=None):
        """
        nba_odds property setter. if a data frame is passed to it sets the
        nba_odds attribute to that df. Otherwise set off the scraping process.
        :params
            df(pandas DataFrame) -> a data frame to set nba_odds to
        """
        if self._nba_odds is not None:
            self._nba_odds = df
        else:
            self._navigate_to_NBA()
            sleep(3)
            markup = self._get_markup()
            self._nba_odds = self._parse_markup_nba(markup)

    def _parse_markup_ncaaf(self, markup):
        """
        universal parse markup function for ncaaf scrapes
        :params
            markup(BeautifulSoup object) -> the html table to be parsed
        return(pandas DataFrame) -> a dataframe containing scraped data.
        """
        header = self.header
        contents = self._get_data(markup, header)
        return pd.DataFrame(data=contents)

    def _parse_markup_ncaam(self, markup):
        """
        universal parse markup function for ncaam scrapes
        :params
            markup(BeautifulSoup object) -> the html table to be parsed
        return(pandas DataFrame) -> a dataframe containing scraped data.
        """
        header = self.header
        contents = self._get_data(markup, header)
        return pd.DataFrame(data=contents)

    def _parse_markup_nba(self, markup):
        """
        universal parse markup function for nba scrapes
        :params
            markup(BeautifulSoup object) -> the html table to be parsed
        return(pandas DataFrame) -> a dataframe containing scraped data.
        """
        header = self.header
        contents = self._get_data(markup, header)
        return pd.DataFrame(data=contents)
