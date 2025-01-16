from domain.Announcement import Announcement
from domain.Tag import Tag
from domain.MenuItem import MenuItem as MenuItemDomain

from model.MenuItem import MenuItem as MenuItemModel

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
                announcement_tags.append(Tag(announcement_tag, "DISIM"))
            # END manage announcement tags

            preview_of_the_announcement_content = pq(announcement).find("p:nth-child(2)").text()

            announcement_to_be_published = Announcement("DISIM", title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, string_of_announcement_tags, preview_of_the_announcement_content)
            announcements_to_be_published.append(announcement_to_be_published)

        return announcements_to_be_published


    def get_menu_items(self):
        domain = "https://www.disim.univaq.it/"

        menu_html = self.get_div_containing_the_menu_from_the_teaching_page()
        menu_html = super().remove_comments_from_html_code(menu_html)
        menu = pq(menu_html)

        menu_item_model = MenuItemModel()
        menu_item_model.remove_all()

        menu_items = []
        for heading_html in menu("h2").items():  # select all <h2> elements
            heading_text = heading_html.text().strip()

            ul = heading_html.next("ul") or heading_html.next().next("ul")    # check if the next element or the one after that
            # following the current <h2> is a <ul>

            if not ul:
                # neither of the two elements following the <h2> is a <ul>
                continue    # ==> skip the current <h2> because it hasn't related links

            heading = MenuItemDomain(None, heading_text, None, None)
            heading_id = menu_item_model.insert(heading)

            # START save all the link related to the current heading
            for anchor_html in ul.find("a").items():
                anchor_name = anchor_html.text().strip()

                anchor_href = anchor_html.attr("href")
                anchor_href = anchor_href if anchor_href.startswith("https://") or anchor_href.startswith("http://") else f'{domain}{anchor_href}'  # prepend
                # the domain to the href, if necessary

                anchor = MenuItemDomain(None, anchor_name, anchor_href, heading_id)

                menu_items.append(anchor)
            # END save all the link related to the current heading

        menu_item_model.bulk_insert(menu_items)


    def get_div_containing_the_menu_from_the_teaching_page(self):
        """ the <div> containing the menu must have the following HTML structure:
                <div class="row">
                    <h2>
                    <ul>
                        <li>
                            <a>

            this function returns a <div> only if it follows the HTML structure mentioned above
        """

        domain = "https://www.disim.univaq.it/"

        teaching_page_url = domain + "didattica.php"
        teaching_page = super().get_webpage(teaching_page_url)

        # iterate over all divs that have 'row' class
        for _ , div in enumerate(teaching_page('div.row').items()):
            if div.find('h1, h2, h3, h4, h5, h6').length > 0:
                # the current <div> has at least one header element (any <h1>, <h2>, <h3>, <h4>, <h5>, <h6>)

                ul = div.find('ul')
                if ul.length > 0:
                    # the current <div> has at least one <ul> element

                    li = ul.find('li')
                    if li.length > 0:
                        # the current <ul> has at least one <li>

                        a = li.find('a')
                        if a.length > 0:
                            # the current <li> has at least one <a>
                            return div.html()

        return None  # ==> there is no div containing the menu within the teaching page


if __name__ == "__main__":
    disim_website_scraper = DISIMwebsiteScraper()
    disim_website_scraper.get_menu_items()





