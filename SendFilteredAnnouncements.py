from telegram.ext import ApplicationBuilder, ContextTypes

from model.User import User as UserModel
from model.UninterestedWebsite import UninterestedWebsite as UninterestedWebsiteModel


class SendFilteredAnnouncements:
    @staticmethod
    def send_announcements_filtered_by_tags_of_interest_to_user(announcements):
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
                for announcement_tag in announcement.get_tags():
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
                    SendFilteredAnnouncements.send_announcements_to_user(announcement, user)

    @staticmethod
    async def send_announcements_to_user(context: ContextTypes.DEFAULT_TYPE, announcement, user):
        pass

    @staticmethod
    def format_message_content(announcement):
        sections = [
            f'''[{announcement.get_title()}]({announcement.link_to_detail_page()})''',
            announcement.get_preview_of_the_announcement_content()
        ]

        return '\n'.join(sections)
