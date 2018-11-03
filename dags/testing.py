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

def make_truth(pairs):
    truth = {}
    for pair in pairs:
        team1 = pair[0]
        team2 = pair[1]
        truth[team1] = team2
        truth[team2] = team1
    return truth

scraper_classes = [InteropScraper, BovadaScraper, SportsBettingScraper, BetOnlineScraper, YouWagerScraper ]
exceptions = 0

frames = {}
scrapers = {}
for scraper in scraper_classes:
    scraped = scraper("ncaaf")
    scrapers[scraped.site] = scraped
    frames[scraped.site] = scraped.ncaaf_odds
    if scraped.sel:
        scraped.driver.quit()


final_key = list(frames.keys())[0]
for key, frame in frames.items():
    if frame.shape[0] > frames[key].shape[0]:
        final_key = key
truth = make_truth(list(frames[final_key]["Teams"]))
print(truth)
for key, frame in frames.items():
    print(scrapers[key].site)
    scrapers[key].set_ncaaf_odds(clean_frame_ncaaf(df=frame, truth=truth))

struct = {scraper.site: scraper.ncaaf_odds for scraper in scrapers.values()}
with open("arb_input.pickle", "wb") as f:
    pickle.dump(struct, f)
