from model.AbstractModel import AbstractModel
from model.UninterestedIn import UninterestedIn as UninterestedInModel

from domain.User import User as UserDomain


class User(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(User, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    @staticmethod
    def insert(chat_id):
        query = '''INSERT INTO user (chat_id) VALUES (:chat_id);'''
        query_parameters = {"chat_id": chat_id}

        return AbstractModel.execute_query(query, query_parameters, True)

    @staticmethod
    def get_all():
        query = '''SELECT * FROM user'''

        results = AbstractModel.execute_query(query)

        users = []
        for result in results:
            user_uninterested_tags = UninterestedInModel.get_user_uninterested_tags(result["ID"])
            users.append(UserDomain(result['chat_id'], user_uninterested_tags))

        return users