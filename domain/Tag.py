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

    # this function is used to compare instances of this class
    def __eq__(self, other_tag):
        if isinstance(other_tag, Tag):
            return self.name == other_tag.get_name() and self.website == other_tag.get_website()

        return False


