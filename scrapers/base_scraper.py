import logging
import time

from utils import paths, headers
from selenium import webdriver


class OddScraper:

    def __init__(self, url, sport, site, sel=False):
        self.url = url
        self.path = paths[sport][site]
        self.header = headers[sport]

        if sel:
            options = webdriver.ChromeOptions()
            #options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            self.driver = webdriver.Chrome(chrome_options=options)
