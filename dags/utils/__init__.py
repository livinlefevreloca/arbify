import logging

from bs4 import BeautifulSoup

logging.basicConfig(level="INFO")


def make_soup(text):
    """
    make soup from html
    :params
        text(string) -> html string
    return(BeautifulSoup object) -> soup of the html string
    """
    return BeautifulSoup(text, 'html.parser')

def make_truth(frames):
    """
    create the ground truth dictinry used to normalize the name columns accross
    all the data frames
    :params
        frames(list) -> list of pandas data frames
    return(dict) -> ground truth name dictionary for normalizing team names
    across data frames
    """
    index = max(frame.shape[0] for frame in frames)
    pairs = frames[index]
    truth = {}
    for pair in pairs:
        team1 = pair[0]
        team2 = pair[1]
        truth[team1] = team2
        truth[team2] = team1
    return truth

base_urls = {"interops": "https://sports.intertops.eu",
             "bovada": "https://www.bovada.lv",
             "betonline": "https://www.betonline.ag",
             "sportsbetting": "https://www.sportsbetting.ag",
             "youwager": "https://www.youwager.eu"}

paths  = {'ncaaf': {"interops": "en/Bets/Competition/1016",
                   "sportsbetting": "sportsbook/football/ncaa",
                   "youwager": "sportsbook",
                   "betonline": "sportsbook",
                   "bovada": "sports/football/college-football"}

             }
headers = {"ncaaf": ("Date", "Teams", "Spread", "Money Line", "Total Points") }
