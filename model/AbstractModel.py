import sqlite3


class AbstractModel:
    @staticmethod
    def execute_query(query, is_a_crud_statement=False):
        try:  # it automatically closes the connection with the DB when not necessary
            with sqlite3.connect("telegram_bot.db") as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                if not is_a_crud_statement:
                    results = cursor.fetchall()
                    return results
        except sqlite3.Error as e:
            print(f"Error while operating with the DB: {e}")
            if not is_a_crud_statement:
                return []

    def create_tables(self):
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
            name text,
            website text);''',
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
            self.execute_query(query, True)


if __name__ == '__main__':
    abstract_model = AbstractModel()
    abstract_model.create_tables()
