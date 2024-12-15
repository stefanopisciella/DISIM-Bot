from model.AbstractModel import AbstractModel

from domain.Tag import Tag as TagDomain


class UninterestedWebsite(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UninterestedWebsite, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern


    @staticmethod
    def insert(user_id, tag_id):
        query = '''INSERT INTO uninterested_in (user_id, tag_id) VALUES (:user_id, :tag_id);'''
        query_parameters = {"user_id": user_id, "tag_id": tag_id}

        return AbstractModel.execute_query(query, query_parameters, True)

    def bulk_insert(self, user_id, user_uninterested_tag_ids):
        for user_uninterested_tag_id in user_uninterested_tag_ids:
            self.insert(user_id, user_uninterested_tag_id)

    @staticmethod
    def get_user_uninterested_tags(user_id):
        query = '''SELECT t.name as name, t.website as website
                   FROM uninterested_in u JOIN tag t ON u.tag_id = t.ID
                   WHERE u.user_id = :user_id;'''

        results = AbstractModel.execute_query(query, {"user_id": user_id}, False)

        user_uninterested_tags = []
        for result in results:
            user_uninterested_tags.append(TagDomain(result['name'], result['website']))

        return  user_uninterested_tags
