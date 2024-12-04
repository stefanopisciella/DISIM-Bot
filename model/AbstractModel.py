import sqlite3


class AbstractModel:
    @staticmethod
    def execute_query(query, query_parameters=None, is_a_crud_statement=False):
        try:  # it automatically closes the connection with the DB when not necessary
            with sqlite3.connect("telegram_bot.db") as conn:
                conn.row_factory = sqlite3.Row  # to enable column name access

                cursor = conn.cursor()

                if query_parameters is not None:
                    cursor.execute(query, query_parameters)
                else:
                    cursor.execute(query)

                if is_a_crud_statement:
                    last_inserted_tuple_id = cursor.lastrowid
                    return last_inserted_tuple_id  # is useful only after executing an INSERT statement
                else:
                    results = cursor.fetchall()
                    return results
        except sqlite3.Error as e:
            print(f"Error while operating with the DB: {e}")

            if is_a_crud_statement:
                return None  # this value is referred to the last_inserted_tuple_id
            else:
                return []

    @staticmethod
    def create_tables():
        queries = ['''
            CREATE TABLE IF NOT EXISTS announcement (
            ID INTEGER PRIMARY KEY,
            website text,
            title text,
            link_to_detail_page text,
            publication_date text,
            reformatted_publication_date text,
            preview_of_the_announcement_content text);''',
        ''' CREATE TABLE IF NOT EXISTS tag (
            ID INTEGER PRIMARY KEY,
            name text NOT NULL CHECK (tag.name <> ''),
            website text NOT NULL CHECK (tag.website <> ''));''',
         '''CREATE TABLE IF NOT EXISTS user (
            ID INTEGER PRIMARY KEY,
            chat_id text);''',
         '''CREATE TABLE IF NOT EXISTS uninterested_in (
            ID INTEGER PRIMARY KEY,
            user_id INTEGER,
            tag_id INTEGER,

            FOREIGN KEY (user_id) REFERENCES user(ID),
            FOREIGN KEY (tag_id) REFERENCES tag(ID));''',
         '''CREATE TABLE IF NOT EXISTS features (
            ID INTEGER PRIMARY KEY,
            tag_id INTEGER,
            announcement_id INTEGER,

            FOREIGN KEY (tag_id) REFERENCES tag(ID),
            FOREIGN KEY (announcement_id) REFERENCES announcement(ID)); ''']

        for query in queries:
            AbstractModel.execute_query(query, None, True)


if __name__ == '__main__':
    AbstractModel.create_tables()