from domain.Announcement import Announcement
from domain.Tag import Tag

from website_scrapers.WebsiteScraper import WebsiteScraper

from pyquery import PyQuery as pq


class ADSUwebsiteScraper(WebsiteScraper):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ADSUwebsiteScraper, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    def __init__(self):
        super().__init__("adsu_db.json")

    def get_announcements(self):
        domain = "https://www.adsuaq.org/"

        news_section_url = domain + "category/news"
        news_section = super().get_webpage(news_section_url)

        announcements = news_section('ul.post_list_ul > li')

        announcements_to_be_published = []
        announcements.reverse()  # order the list of announcements from the least recent to the most recent
        for announcement in announcements:
            publication_date = pq(announcement).find("div.stm_post_details > ul > li.post_date").text()
            reformatted_publication_date = super().reformat_date(publication_date)
            link_to_detail_page = pq(announcement).find("h4 > a").attr("href")

            if not super().check_if_the_announcement_must_be_scraped(reformatted_publication_date, link_to_detail_page):
                # the current announcement has already been scraped ==> don't continue scraping the current announcement
                continue

            title = pq(announcement).find("h4 > a").text()

            # START manage announcement tags
            string_of_announcement_tags = pq(announcement).find("div.stm_post_details > ul > li.post_cat > span").text()

            announcement_tags = []
            for announcement_tag in string_of_announcement_tags.split(', '):
                announcement_tags.append(Tag(announcement_tag, "ADSU"))
            # END manage announcement tags

            preview_of_the_announcement_content = pq(announcement).find("div.post_excerpt > p").text()

            announcement_to_be_published = Announcement("ADSU", title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, string_of_announcement_tags, preview_of_the_announcement_content)
            announcements_to_be_published.append(announcement_to_be_published)

        return announcements_to_be_published