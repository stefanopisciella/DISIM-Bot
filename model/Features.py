from model.AbstractModel import AbstractModel

from domain.Features import Features as FeaturesDomain

class Features(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Features, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    @staticmethod
    def insert(features: FeaturesDomain):
        query = '''INSERT INTO features (tag_id, announcement_id) VALUES (:tag_id, :announcement_id);'''
        query_parameters = {"tag_id": features.get_tag_id(), "announcement_id": features.get_announcement_id()}

        return AbstractModel.execute_query(query, query_parameters, True)
