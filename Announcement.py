class Announcement:

    def __init__(self, website, title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, preview_of_the_announcement_content):
        self.website = website
        self.title = title
        self.link_to_detail_page = link_to_detail_page
        self.publication_date = publication_date
        self.reformatted_publication_date = reformatted_publication_date
        self.announcement_tags = announcement_tags
        self.preview_of_the_announcement_content = preview_of_the_announcement_content

    def get_website(self):
        return self.website

    def set_website(self, website):
        self.website = website

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_link_to_detail_page(self):
        return self.link_to_detail_page

    def set_link_to_detail_page(self, link_to_detail_page):
        self.link_to_detail_page = link_to_detail_page

    def get_publication_date(self):
        return self.publication_date

    def set_publication_date(self, publication_date):
        self.publication_date = publication_date

    def get_reformatted_publication_date(self):
        return self.reformatted_publication_date

    def set_reformatted_publication_date(self, reformatted_publication_date):
        self.reformatted_publication_date = reformatted_publication_date

    def get_announcement_tags(self):
        return self.announcement_tags

    def set_announcement_tags(self, announcement_tags):
        self.announcement_tags = announcement_tags

    def get_preview_of_the_announcement_content(self):
        return self.preview_of_the_announcement_content

    def set_preview_of_the_announcement_content(self, preview_of_the_announcement_content):
        self.preview_of_the_announcement_content = preview_of_the_announcement_content