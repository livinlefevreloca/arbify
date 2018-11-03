from scrapers.bovada import BovadaScraper
from scrapers.intertops import InteropScraper
from scrapers.betonline import BetOnlineScraper
from scrapers.youwager import YouWagerScraper
from scrapers.sportsbetting import SportsBettingScraper
from utils import make_truth
from clean import clean_frame_ncaaf


def get_bovada_ncaaf(**context):
    sport = context["params"]["sport"]
    scraper = BovadaScraper(sport=sport)
    scraper.set_ncaaf_odds()
    return scraper

def get_interops_ncaaf(**context):
    sport = context["params"]["sport"]
    scraper = InteropScraper(sport=sport)
    scraper.set_ncaaf_odds()
    return scraper

def get_betonline_ncaaf(**context):
    sport = context["params"]["sport"]
    scraper = BetOnlineScraper(sport=sport)
    scraper.set_ncaaf_odds()
    return scraper

def get_youwager_ncaaf(**context):
    sport = context["params"]["sport"]
    scraper = YouWagerScraper(sport=sport)
    scraper.set_ncaaf_odds()
    return scraper

def get_sportsbetting_ncaaf(**context):
    sport = context["params"]["sport"]
    scraper = SportsBettingScraper(sport=sport)
    scraper.set_ncaaf_odds()
    return scraper

def make_true_names(**context):
    task_id = context["params"]["tasks"]
    dfs = [context["ti"].xcom_pull(task_ids=task).ncaaf_odds for task in tasks]
    return make_truth(dfs)

def clean_ncaaf(**context):
    task = context["params"]["task"]
    truth = context["ti"].xcom_pull("get_true_names_task")
    scraper = context["ti"].xcom_pull(task_id)
    new_df = clean_ncaaf(scraper.ncaaf_odds, truth)
    scraper.set_ncaaf_odds(df=new_df)
    return scraper

def detect(**context):
    tasks = context["params"]["tasks"]
    scrapers = [context["ti"].xcom_pull(task) for task in tasks]
    keyed_scrapers = {scraper.site: scraper for scraper in scrapers}
    keyed_dfs = {scraper.site: scraper.ncaaf_odds for scraper in scrapers}
    detections = detect(keyed_dfs)
