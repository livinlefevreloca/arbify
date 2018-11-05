from scrapers.betonline import BetOnlineScraper
from scrapers.youwager import YouWagerScraper
from scrapers.bovada import BovadaScraper
from scrapers.interops import InteropScraper
from scrapers.sports_betting import SportsBettingScraper
from clean import clean_frame_ncaaf
import pickle

# betonline = BetOnlineScraper("ncaaf")
# lines = betonline.ncaaf_odds
# print(clean_frame_ncaaf(lines))
# betonline.driver.quit()
# youwager = YouWagerScraper("ncaaf")
# lines = youwager.ncaaf_odds
# print(clean_frame_ncaaf(lines))
# youwager.driver.quit()
# bovada = BovadaScraper("ncaaf")
# lines = bovada.ncaaf_odds
# print(clean_frame_ncaaf(lines))
# bovada.driver.quit()
# interops = InteropScraper("ncaaf")
# lines = interops.ncaaf_odds
# print(clean_frame_ncaaf(lines))
# interops.driver.quit()
# sportsbetting = SportsBettingScraper("ncaaf")
# lines = sportsbetting.ncaaf_odds
# print(clean_frame_ncaaf(lines))
