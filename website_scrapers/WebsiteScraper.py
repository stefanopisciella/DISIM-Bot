from abc import ABC, abstractmethod

import requests, json

from pyquery import PyQuery as pq

class WebsiteScraper(ABC): # this is a formal interface
    def __init__(self, db_filename):
        self.db_filename = db_filename

    @staticmethod
    @abstractmethod
    def get_announcements(self):
        pass

    @staticmethod
    def reformat_date(original_date):
        new_date = original_date.replace(',', '')
        new_date = new_date.split(' ')

        year = new_date[-1]
        month = new_date[-2]
        day = new_date[-3]

        mesi = [
            "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio",
            "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre",
            "Novembre", "Dicembre"
        ]

        for i in range(12):
            if mesi[i] == month:
                month = i + 1
                break

        month = '0' + str(month) if int(month) < 10 else month
        day = '0' + str(day) if int(day) < 10 else day

        return f"{year}-{month}-{day}"

    @staticmethod
    def get_webpage(url):
        response = requests.get(url)
        return pq(response.content)

    @staticmethod
    def debug_by_printing_prettified_json(list_of_announcement_objects):
        list_of_announcement_dictionaries = []

        for announcement_object in list_of_announcement_objects:
            # START conversion of announcement tags from objects to dictionaries
            list_of_tag_objects_relative_to_the_announcement = announcement_object.get_announcement_tags()

            list_of_tag_dictionaries_relative_to_the_announcement = []
            for tag_object in list_of_tag_objects_relative_to_the_announcement:
                tag_dictionary = tag_object.__dict__
                list_of_tag_dictionaries_relative_to_the_announcement.append(tag_dictionary)

            announcement_object.set_announcement_tags(list_of_tag_dictionaries_relative_to_the_announcement)
            # END conversion of announcement tags from objects to dictionaries

            announcement_dictionary = announcement_object.__dict__
            list_of_announcement_dictionaries.append(announcement_dictionary)

        print(json.dumps(list_of_announcement_dictionaries, indent=4))

    def check_if_the_announcement_must_be_scraped(self, announcement_publication_date, announcement_url):
        with open(self.db_filename, 'r', encoding='utf-8') as json_file:
            json_content = json.load(json_file)

            if announcement_publication_date < json_content["last_scraped_announcement_publication_date"]:
                # the announcement to be checked is older than the last scraped announcement
                return False
            elif announcement_publication_date > json_content["last_scraped_announcement_publication_date"]:
                # the announcement to be checked is newer than the last scraped announcement

                json_content["last_scraped_announcement_publication_date"] = announcement_publication_date
                json_content["announcements_urls"] = [announcement_url]
                WebsiteScraper.write_db_file(self.db_filename, json_content)
                return True
            elif announcement_publication_date == json_content["last_scraped_announcement_publication_date"]:
                # retrive all the urls relative to all announcement published on the disim website on the day of announcement_publication_date
                announcements_urls = json_content["announcements_urls"]

                if announcement_url in announcements_urls:
                    # the announcement to be checked has been already scraped
                    return False
                else:
                    # the announcement to be checked hasn't been scraped yet

                    json_content["announcements_urls"].append(announcement_url)
                    WebsiteScraper.write_db_file(self.db_filename, json_content)
                    return True

    @staticmethod
    def write_db_file(db_filename, data):
        with open(db_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)