from model.AbstractModel import AbstractModel

from domain.UninterestedIn import UninterestedIn as UninterestedInDomain


class UninterestedIn(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UninterestedIn, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    @staticmethod
    def insert(uninterested_in: UninterestedInDomain):
        query = '''INSERT INTO uninterested_in (user_id, tag_id) VALUES (:user_id, :tag_id);'''
        query_parameters = {"user_id": uninterested_in.get_user_id(), "tag_id": uninterested_in.get_tag_id()}

        return AbstractModel.execute_query(query, query_parameters, True)

    def bulk_insert(self, uninterested_in_list):
        for uninterested_in in uninterested_in_list:
            self.insert(uninterested_in)