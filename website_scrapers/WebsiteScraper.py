from abc import ABC, abstractmethod

import requests, json

from pyquery import PyQuery as pq

class WebsiteScraper(ABC): # this is a formal interface
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
    def debug_by_printing_prettified_json(announcement):
        print(json.dumps(announcement, indent=4))

    @staticmethod
    def check_if_the_announcement_must_be_scraped(is_a_disim_announcement, announcement_publication_date, announcement_url):
        json_filename = "disim_db.json" if is_a_disim_announcement else "adsu_db.json"

        with open(json_filename, 'r', encoding='utf-8') as json_file:
            json_content = json.load(json_file)

            if announcement_publication_date < json_content["last_scraped_announcement_publication_date"]:
                # the announcement to be checked is older than the last scraped announcement
                return False
            elif announcement_publication_date > json_content["last_scraped_announcement_publication_date"]:
                # the announcement to be checked is newer than the last scraped announcement

                json_content["last_scraped_announcement_publication_date"] = announcement_publication_date
                json_content["announcements_urls"] = [announcement_url]
                WebsiteScraper.write_db_file(json_filename, json_content)
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
                    WebsiteScraper.write_db_file(json_filename, json_content)
                    return True

    @staticmethod
    def write_db_file(json_filename, data):
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)