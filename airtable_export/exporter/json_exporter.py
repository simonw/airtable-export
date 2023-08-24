import json


class JsonExporter:
    @staticmethod
    def generate_file(file_path, records, table_name):
        filename = f"{table_name}.json"
        dumped = json.dumps(records, sort_keys=True, indent=4)
        json_filepath = file_path / filename
        json_filepath.write_text(dumped, "utf-8")
        return json_filepath
