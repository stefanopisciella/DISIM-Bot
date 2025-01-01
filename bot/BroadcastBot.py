import logging
from telegram import Bot
from telegram.error import TelegramError

from model.User import User as UserModel
from model.UninterestedWebsite import UninterestedWebsite as UninterestedWebsiteModel

import configuration_file as conf


class BroadcastBot:
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.bot = Bot(token=conf.TELEGRAM_BOT_TOKEN)

            # START set logging
            logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.INFO
            )
            cls._instance.logger = logging.getLogger(__name__)
            # END set logging

        return cls._instance

    # END singleton design pattern

    async def send_announcements_filtered_by_tags_of_interest_to_user(self, announcements):
        users = UserModel.get_all()
        uninterested_website_model = UninterestedWebsiteModel()

        for user in users:
            user_uninterested_websites = uninterested_website_model.get_user_uninterested_websites(user.get_user_id())

            for announcement in announcements:
                interested = True  # ==> user interested in the current announcement

                # START check if the website of the current announcement is of user interest
                if announcement.get_website() in user_uninterested_websites:
                    break
                # END check if the website of the current announcement is of user interest

                # START check if all tags of the current announcement are of user interest
                for announcement_tag in announcement.get_announcement_tags():
                    if not interested:
                        break

                    for user_uninterested_tag in user.get_uninterested_tags():
                        if announcement_tag.equals(user_uninterested_tag):
                            # the current announcement contains a tag that is not of interest to the user ==> don't
                            # send the current announcement to the current user
                            interested = False  # ==> user disinterested in the current announcement
                            break
                # END check if all tags of the current announcement are of user interest

                if interested:
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

        sections = [
            f'''<a href="{announcement_link_to_detail_page}">{announcement_title}</a>''',  # title and link
            announcement.get_preview_of_the_announcement_content(),  # preview of the announcement
            f'''Tags: '''
        ]

        return '\n'.join(sections)
