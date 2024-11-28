from model.AbstractModel import AbstractModel


class Announcement(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Announcement, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    def insert(self, announcement):
        query = ''''''
        # TODO continue to implement this function
        pass