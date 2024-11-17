from website_scrapers.WebsiteScraper import WebsiteScraper
from website_scrapers.DISIMwebsiteScraper import DISIMwebsiteScraper
from website_scrapers.ADSUwebsiteScraper import ADSUwebsiteScraper

import configuration_file as conf

import time

SECONDS_IN_ONE_HOUR = 3600

if __name__ == '__main__':
    disim = DISIMwebsiteScraper()
    adsu = ADSUwebsiteScraper()

    while True:
        announcements_to_be_published = disim.get_announcements()
        announcements_to_be_published.extend(adsu.get_announcements())

        WebsiteScraper.debug_by_printing_prettified_json(announcements_to_be_published)

        time.sleep(conf.HOURS_BETWEEN_SCRAPING * SECONDS_IN_ONE_HOUR)