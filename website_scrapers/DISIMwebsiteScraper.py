from Announcement import Announcement
from Tag import Tag

from website_scrapers.WebsiteScraper import WebsiteScraper

from pyquery import PyQuery as pq


class DISIMwebsiteScraper(WebsiteScraper):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DISIMwebsiteScraper, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern
    
    def __init__(self):
        super().__init__("disim_db.json")

    @staticmethod
    def reformat_url(original_url):
        first_slash = original_url.find('/')
        second_slash = original_url.find('/', first_slash + 1)
        return original_url[:second_slash]

    """
    @staticmethod
    def get_announcement_tags(tags):
        text_of_tags = []
        for tag in tags:
            text_of_tags.append(pq(tag).text())

        return text_of_tags
    """

    def get_announcements(self):
        domain = "https://www.disim.univaq.it/"

        homepage_url = domain + "index"
        homepage = super().get_webpage(homepage_url)

        announcements = homepage('#annunci > div.two-thirds.column > div.row')

        announcements_to_be_published = []
        announcements.reverse()  # order the list of announcements from the least recent to the most recent
        for announcement in announcements:
            publication_date = pq(announcement).find("p.post_meta > span.calendar").text()
            reformatted_publication_date = super().reformat_date(publication_date)
            link_to_detail_page = domain + DISIMwebsiteScraper.reformat_url(pq(announcement).find("h5 > a").attr("href"))

            if not super().check_if_the_announcement_must_be_scraped(reformatted_publication_date, link_to_detail_page):
                # the current announcement has already been scraped ==> don't continue scraping the current announcement
                continue

            title = pq(announcement).find("h5 > a").text()

            # START manage announcement tags
            string_of_announcement_tags = pq(announcement).find("p.post_meta > span.tags > a").text()

            announcement_tags = []
            for announcement_tag in string_of_announcement_tags.split(', '):
                announcement_tags.append(Tag(announcement_tag, "disim"))
            # END manage announcement tags

            preview_of_the_announcement_content = pq(announcement).find("p:nth-child(2)").text()

            announcement_to_be_published = Announcement("disim", title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, preview_of_the_announcement_content)
            announcements_to_be_published.append(announcement_to_be_published)

        return announcements_to_be_published