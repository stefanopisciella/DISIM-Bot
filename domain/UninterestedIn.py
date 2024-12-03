class UninterestedIn:

    def __init__(self, user_id, tag_id):
        self.user_id = user_id
        self.tag_id = tag_id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_tag_id(self):
        return self.tag_id

    def set_tag_id(self, tag_id):
        self.tag_id = tag_id

