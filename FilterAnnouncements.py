from model.User import User as UserModel

class FilterAnnouncements:
    @staticmethod
    def filter_announcements_by_tags_of_interest_to_user(announcements):
        users = UserModel.get_all()

        for user in users:
            for announcement in announcements:
                for announcement_tag in announcement.get_tags():
                    for user_uninterested_tag in user.get_uninterested_tags():
                        if not announcement_tag.equals(user_uninterested_tag):
                            FilterAnnouncements.send_announcements_to_user(announcement, user)


    @staticmethod
    def send_announcements_to_user(announcement, user):
        # TODO implement this function as soon as the Telegram bot is implemented
        pass
