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
        query = '''INSERT INTO user (chat_id)
                   VALUES (:chat_id)
                   ON CONFLICT (chat_id) DO NOTHING;'''
        query_parameters = {"chat_id": chat_id}

        return AbstractModel.execute_query(query, query_parameters, True)

    @staticmethod
    def get_all():
        query = '''SELECT * FROM user'''

        results = AbstractModel.execute_query(query)

        users = []
        for result in results:
            user_id = result["ID"]

            user_uninterested_tags = UninterestedInModel.get_user_uninterested_tags(user_id)
            users.append(UserDomain(user_id, result['chat_id'], user_uninterested_tags))

        return users

    @staticmethod
    def get_user_id_by_his_chat_id(chat_id):
        query = '''SELECT ID
                   FROM user
                   WHERE chat_id = :chat_id; '''

        user_id = AbstractModel.execute_query(query, query_parameters={"chat_id": chat_id})
        return user_id[0][0] if user_id else None