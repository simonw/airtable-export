import json


class NDJsonExporter:
    @staticmethod
    def generate_file(output, records, table_name):
        filename = f"{table_name}.ndjson"
        dumped = "\n".join(json.dumps(r, sort_keys=True) for r in records)
        ndjson_filepath = output / filename
        ndjson_filepath.write_text(dumped, "utf-8")
        return ndjson_filepath.name
