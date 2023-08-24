import sqlite_utils


class SqlLiteRepository:
    MAX_RECORDS = 100

    def __init__(self, sqlite_filepath):
        self.db = sqlite_utils.Database(sqlite_filepath)

    def write(self, table_name, records):
        for index in range(0, len(records), self.MAX_RECORDS):
            records_to_insert = records[index:index + self.MAX_RECORDS]
            primary_key = "airtable_id"
            self.db[table_name].insert_all(records_to_insert, pk=primary_key, replace=True, alter=True)
