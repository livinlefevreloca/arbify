import logging
import time

from selenium import webdriver


class OddScraper:

    def __init__(self, url):
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.base_url = url
