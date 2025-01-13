class MenuItem:
    def __init__(self, name, link, parent_id):
        self.name = name
        self.link = link
        self.parent_id = parent_id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_link(self):
        return self.link

    def set_link(self, link):
        self.link = link

    def get_parent_id(self):
        return self.parent_id

    def set_parent_id(self, parent_id):
        self.parent_id = parent_id
