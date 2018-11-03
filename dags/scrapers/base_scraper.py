import logging
import time
import pandas as pd

from utils import paths, headers, base_urls
from selenium import webdriver
from time import sleep


class OddScraper:

    def __init__(self, sport, site, sel=False):
        """
        base scraper contstructor hold information about the scraper. All other
        scrapers inherit from this scraper

        :params
            sport(string) -> identify the sport to parsed for
            site(string) -> identify the site to be scraped
            sel(boo) -> is selenium being used
        """
        self.url = base_urls[site]
        self.path = paths[sport][site]
        self.header = headers[sport]
        self.site = site
        self.sel = sel
        self.arbs = []
        self._ncaaf_odds = None

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
            markup = self._get_markup_ncaaf()
            self._ncaaf_odds = self._parse_markup_ncaaf(markup)

    def _parse_markup_ncaaf(self, markup):
        """
        universal parse markup function for ncaaf scrapes
        :params
            markup(BeautifulSoup object) -> the html table to be parsed
        return(pandas DataFrame) -> a dataframe containing scraped data.
        """
        header = self.header
        contents = self._get_data_ncaaf(markup, header)
        return pd.DataFrame(data=contents)
