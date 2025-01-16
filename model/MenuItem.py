from model.AbstractModel import AbstractModel

from domain.MenuItem import MenuItem as MenuItemDomain


class MenuItem(AbstractModel):
    # START singleton design pattern
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MenuItem, cls).__new__(cls)
        return cls._instance
    # END singleton design pattern

    @staticmethod
    def insert(menu_item: MenuItemDomain):
        query = '''INSERT INTO menu_item (name, link, parent_id) VALUES (:name, :link, :parent_id);'''
        query_parameters = {"name": menu_item.get_name(), "link": menu_item.get_link(), "parent_id": menu_item.get_parent_id()}

        return AbstractModel.execute_query(query, query_parameters, True)

    def bulk_insert(self, menu_items):
        for menu_item in menu_items:
            self.insert(menu_item)

    @staticmethod
    def remove_all():
        query = '''DELETE FROM menu_item WHERE 1;'''

        return AbstractModel.execute_query(query=query, is_a_crud_statement=True)

    @staticmethod
    def get_all_first_level_menu_items():
        query = '''SELECT ID, name
                   FROM menu_item
                   WHERE parent_id IS NULL;'''

        results = AbstractModel.execute_query(query)

        items = []
        for result in results:
            item = MenuItemDomain(result['ID'], result['name'], None, None)
            items.append(item)

        return items

