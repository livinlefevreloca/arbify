import logging

from bs4 import BeautifulSoup

logging.basicConfig(level="INFO")


def make_soup(text):
    return BeautifulSoup(text, 'html.parser')


paths  ={'ncaaf': {"interops": "en/Bets/Competition/1016",
                   "sportsbetting": "sportsbook/football/ncaa",
                   "youwager": "sportsbook",
                   "5dimes": "",
                   "bovada": "sports/football/college-football"}

             }
headers = {"ncaaf": ("Date", "Teams", "Spread", "Money Line", "Total Points") }

def translate_fraction(string):
    frac_bytes = b'\xc2\xbd'
    dec_bytes = b'.5'
    return string.encode().replace(frac_bytes, dec_bytes).decode
