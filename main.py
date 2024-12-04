from website_scrapers.DISIMwebsiteScraper import DISIMwebsiteScraper
from website_scrapers.ADSUwebsiteScraper import ADSUwebsiteScraper

from SendFilteredAnnouncements import SendFilteredAnnouncements

from model.Announcement import Announcement as AnnouncementModel

import configuration_file as conf

import time

SECONDS_IN_ONE_HOUR = 3600

'''
def test_the_insertion_into_db_of_user_data_and_disinterests():  # this function is temporary, so it will be deleted
    user_model = UserModel()
    uninterested_in_model = UninterestedInModel()

    # START user #1
    user1 = UserDomain("000000001")
    user1_id = user_model.insert(user1)

    user1_uninterested_in =[
        UninterestedInDomain(user1_id, 1),
        UninterestedInDomain(user1_id, 2)
    ]

    uninterested_in_model.bulk_insert(user1_uninterested_in)
    # END user #1
'''

if __name__ == '__main__':
    disim = DISIMwebsiteScraper()
    adsu = ADSUwebsiteScraper()

    while True:
        # START scrape announcements from "disim" and "adsu" websites
        announcements_to_be_published = disim.get_announcements()
        announcements_to_be_published.extend(adsu.get_announcements())

        # WebsiteScraper.debug_by_printing_prettified_json(announcements_to_be_published)
        # END scrape announcements from "disim" and "adsu" websites

        # START insert announcements into SQLite DB
        announcement_model = AnnouncementModel()
        announcement_model.bulk_insert(announcements_to_be_published)
        # END insert announcements into SQLite DB

        SendFilteredAnnouncements.send_announcements_filtered_by_tags_of_interest_to_user(announcements_to_be_published)

        del announcements_to_be_published  # free up RAM

        time.sleep(conf.HOURS_BETWEEN_SCRAPING * SECONDS_IN_ONE_HOUR)