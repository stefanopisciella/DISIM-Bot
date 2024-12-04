class Tag:

    def __init__(self, name, website):
        self.name = name.strip()
        self.website = website

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name.strip()

    def get_website(self):
        return self.website

    def set_website(self, website):
        self.website = website

    def equals(self, other_tag):
        return self.name == other_tag.name and self.website == other_tag.website


