from website_scrapers.WebsiteScraper import WebsiteScraper
from website_scrapers.DISIMwebsiteScraper import DISIMwebsiteScraper
from website_scrapers.ADSUwebsiteScraper import ADSUwebsiteScraper


if __name__ == '__main__':
    disim = DISIMwebsiteScraper()
    adsu = ADSUwebsiteScraper()

    announcements_to_be_published = disim.get_announcements()
    announcements_to_be_published.extend(adsu.get_announcements())

    WebsiteScraper.debug_by_printing_prettified_json(announcements_to_be_published)