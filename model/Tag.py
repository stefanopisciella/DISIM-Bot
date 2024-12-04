from model.AbstractModel import AbstractModel

from domain.Tag import Tag as TagDomain


class Tag(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Tag, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    def insert(self, tag: TagDomain):
        tag_id = self.get_the_id_of_the_passed_tag_if_already_exists(tag)

        if tag_id:
            return tag_id

        query = '''INSERT INTO tag (name, website) VALUES (:name, :website);'''
        query_parameters = {"name": tag.get_name(), "website": tag.get_website()}

        return AbstractModel.execute_query(query, query_parameters, True)

    @staticmethod
    def get_the_id_of_the_passed_tag_if_already_exists(tag: TagDomain):
        query = '''SELECT ID
                   FROM tag t
                   WHERE t.website = :website AND t.name COLLATE NOCASE = :name;
                '''
        query_parameters = {"website": tag.get_website(), "name": tag.get_name()}

        tag_id = AbstractModel.execute_query(query, query_parameters)
        return tag_id[0][0] if tag_id else None
