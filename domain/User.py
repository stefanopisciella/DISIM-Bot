class User:

    def __init__(self, user_id, chat_id, uninterested_tags):
        self.user_id = user_id
        self.chat_id = chat_id
        self.uninterested_tags = uninterested_tags

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_chat_id(self):
        return self.chat_id

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def get_uninterested_tags(self):
        return self.uninterested_tags

    def set_uninterested_tags(self, uninterested_tags):
        self.uninterested_tags = uninterested_tags

