from model.AbstractModel import AbstractModel

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
    def insert(user: UserDomain):
        query = '''INSERT INTO user (chat_id) VALUES (:chat_id);'''
        query_parameters = {"chat_id": user.get_chat_id()}

        return AbstractModel.execute_query(query, query_parameters, True)