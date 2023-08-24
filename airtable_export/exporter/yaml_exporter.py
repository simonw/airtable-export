import yaml


class YamlExporter:
    def __init__(self):
        yaml.add_representer(str, str_representer)

    @staticmethod
    def generate_file(file_path, records, table_name):
        filename = f"{table_name}.yml"
        dumped = yaml.dump(records, sort_keys=True)
        yaml_filepath = file_path / filename
        yaml_filepath.write_text(dumped, "utf-8")
        return yaml_filepath


def str_representer(dumper, data):
    try:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    except TypeError:
        pass
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)
