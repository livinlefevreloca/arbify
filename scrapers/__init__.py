from bovada import BovadaScraper


scraper = BovadaScraper("https://www.bovada.lv", "ncaaf", "bovada", sel=True)
print(scraper._get_NCAAF_lines())
