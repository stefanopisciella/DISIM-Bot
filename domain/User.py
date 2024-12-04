class User:

    def __init__(self, chat_id, uninterested_tags):
        self.chat_id = chat_id
        self.uninterested_tags = uninterested_tags

    def get_chat_id(self):
        return self.chat_id

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def get_uninterested_tags(self):
        return self.uninterested_tags

    def set_uninterested_tags(self, uninterested_tags):
        self.uninterested_tags = uninterested_tags

