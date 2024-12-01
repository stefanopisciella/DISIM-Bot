from model.AbstractModel import AbstractModel
from model.Tag import Tag as TagModel
from model.Features import Features as FeaturesModel

from domain.Announcement import Announcement as AnnouncementDomain
from domain.Features import Features


class Announcement(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Announcement, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    def insert(self, announcement: AnnouncementDomain):
        query = '''INSERT INTO announcement (website, title, link_to_detail_page, publication_date, reformatted_publication_date, preview_of_the_announcement_content) 
                   VALUES (:website, :title, :link_to_detail_page, :publication_date, :reformatted_publication_date, :preview_of_the_announcement_content);'''

        query_parameters = {"website": announcement.get_website(),
                            "title": announcement.get_title(),
                            "link_to_detail_page": announcement.get_link_to_detail_page(),
                            "publication_date": announcement.get_publication_date(),
                            "reformatted_publication_date": announcement.get_reformatted_publication_date(),
                            "preview_of_the_announcement_content": announcement.get_preview_of_the_announcement_content()}
        last_inserted_announcement_id = AbstractModel.execute_query(query, query_parameters, True)

        # START manage announcement tags
        announcement_tags = announcement.get_announcement_tags()

        tag_model = TagModel()
        features_model = FeaturesModel()
        for announcement_tag in announcement_tags:
            last_inserted_announcement_tag_id = tag_model.insert(announcement_tag) # insert the current tag into the tag table

            features = Features(last_inserted_announcement_tag_id, last_inserted_announcement_id)
            features_model.insert(features)
        # END manage announcement tags

        return  last_inserted_announcement_id

    def bulk_insert(self, announcements):
        for announcement in announcements:
            self.insert(announcement)