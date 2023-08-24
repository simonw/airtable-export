import csv


class CsvExporter:
    @staticmethod
    def generate_file(file_path, records, table_name):
        filename = f"{table_name}.csv"
        csv_filepath = file_path / filename
        with open(csv_filepath, 'w', encoding='UTF8') as file:
            writer = csv.writer(file)
            header = records[0].keys()
            writer.writerow(header)
            for record in records:
                data = [f"{value}" for value in record.values()]
                writer.writerow(data)
        return csv_filepath.name
