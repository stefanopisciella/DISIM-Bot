from model.User import User as UserModel

class SendFilteredAnnouncements:
    @staticmethod
    def filter_announcements_by_tags_of_interest_to_user(announcements):
        users = UserModel.get_all()

        for user in users:
            for announcement in announcements:
                for announcement_tag in announcement.get_tags():
                    for user_uninterested_tag in user.get_uninterested_tags():
                        if announcement_tag.equals(user_uninterested_tag):
                            # the current announcement contains a tag that is not of interest to the user ==> don't
                            # send the current announcement to the current user
                            break
                        SendFilteredAnnouncements.send_announcements_to_user(announcement, user)

    @staticmethod
    def send_announcements_to_user(announcement, user):
        # TODO implement this function as soon as the Telegram bot is implemented
        pass
