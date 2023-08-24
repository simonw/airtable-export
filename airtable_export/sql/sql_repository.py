import sqlite_utils

class SqlLiteRepository:
    def __init__(self, sqlite_filepath):
        self.db = sqlite_utils.Database(sqlite_filepath)

    def write(self, table_name, records):
        self.db[table_name].insert_all(records, pk="airtable_id", replace=True, alter=True)

