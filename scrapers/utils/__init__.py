import logging

from bs4 import BeautifulSoup
from functools import wraps

logging.basicConfig(level="INFO")

def safety_net(f):
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            logging.info("The exception occured in {}".format(f.__name__))
            return None
    return wrapper


def make_soup(text):
    return BeautifulSoup(text, 'html.parser')    
