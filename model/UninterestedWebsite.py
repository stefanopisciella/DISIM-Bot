from model.AbstractModel import AbstractModel


class UninterestedWebsite(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UninterestedWebsite, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    @staticmethod
    def insert(user_id, website):
        query = '''INSERT INTO uninterested_website (user_id, website) VALUES (:user_id, :website);'''
        query_parameters = {"user_id": user_id, "website": website}

        return AbstractModel.execute_query(query, query_parameters, True)

    @staticmethod
    def get_user_uninterested_websites(user_id):
        query = '''SELECT website
                   FROM uninterested_website
                   WHERE user_id = :user_id ;'''
        results = AbstractModel.execute_query(query, {"user_id": user_id}, False)

        return AbstractModel.get_array_column_from_two_dimensional_array(results, "website")

    @staticmethod
    def remove_uninterested_websites_by_user_id(user_id):
        query = '''DELETE FROM uninterested_website 
                   WHERE user_id = :user_id; '''

        AbstractModel.execute_query(query, {"user_id": user_id}, True)