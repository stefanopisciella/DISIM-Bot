import logging
from telegram import Bot
from telegram.error import TelegramError

import time
import asyncio

from website_scrapers.DISIMwebsiteScraper import DISIMwebsiteScraper
from website_scrapers.ADSUwebsiteScraper import ADSUwebsiteScraper

from model.Announcement import Announcement as AnnouncementModel
from model.User import User as UserModel
from model.UninterestedWebsite import UninterestedWebsite as UninterestedWebsiteModel

import configuration_file as conf


class BroadcastBot:
    # START constants
    SECONDS_IN_ONE_HOUR = 3600
    # END constants

    def __init__(self):
        self.bot = Bot(token=conf.TELEGRAM_BOT_TOKEN)

        # START set logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        # END set logging

    async def run(self):
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

            broadcast_bot = BroadcastBot()
            await broadcast_bot.send_announcements_filtered_by_tags_of_interest_to_user(announcements_to_be_published)

            del announcements_to_be_published  # free up RAM

            time.sleep(conf.HOURS_BETWEEN_SCRAPING * self.SECONDS_IN_ONE_HOUR)

    async def send_announcements_filtered_by_tags_of_interest_to_user(self, announcements):
        users = UserModel.get_all()
        uninterested_website_model = UninterestedWebsiteModel()

        for user in users:
            user_uninterested_websites = uninterested_website_model.get_user_uninterested_websites(user.get_user_id())
            user_uninterested_tags = user.get_uninterested_tags()

            for announcement in announcements:
                # START check if the website of the current announcement is of user interest
                if announcement.get_website() in user_uninterested_websites:
                    continue  # ==> skip the check of the announcement tags and don't send the current announcement
                # END check if the website of the current announcement is of user interest

                # START check the tags of the current announcement
                interested = False
                for announcement_tag in announcement.get_announcement_tags():
                    if announcement_tag not in user_uninterested_tags:
                        # there is at least one announcement tag that is of interest to the current user ==> send this
                        # announcement to the current user

                        # the comparison between the current tag of the announcement and the list of tags not of interest
                        # to the user is made possible thanks to the definition of the __eq__ function within the Tag
                        # class

                        interested = True
                        break
                # END check the tags of the current announcement

                if interested:
                    # the website of the current announcement is of interest to the user AND not all announcement tags
                    # are uninteresting to the user

                    # START send the announcement
                    try:
                        await self.bot.send_message(
                            chat_id=user.get_chat_id(),
                            text=BroadcastBot.format_message_content(announcement),
                            parse_mode='HTML'
                        )
                    except TelegramError as e:
                        self.logger.error(f"Failed to send message to user {user.get_chat_id()}: {e}")
                    # END send the announcement

    @staticmethod
    def format_message_content(announcement):
        announcement_title = announcement.get_title()
        announcement_link_to_detail_page = announcement.get_link_to_detail_page()
        string_of_announcement_tags = announcement.get_string_of_announcement_tags()
        announcement_website = announcement.get_website()

        sections = [
            f'''<a href="{announcement_link_to_detail_page}">{announcement_title}</a>''',  # title and link
            announcement.get_preview_of_the_announcement_content(),
            '\n',
            f'''🌐 <i>Sito</i>: {announcement_website}''',
            f'''🏷 <i>Tags</i>: {string_of_announcement_tags}'''
        ]

        return '\n'.join(sections)


if __name__ == '__main__':
    bot = BroadcastBot()
    asyncio.run(bot.run())




