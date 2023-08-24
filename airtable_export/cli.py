import click
import pathlib

import yaml as yaml_

from airtable_export.airtable.airtable_client import AirtableClient
from airtable_export.logger.click_logger import ClickLogger
from airtable_export.exporter.json_exporter import JsonExporter
from airtable_export.exporter.nd_json_exporter import NDJsonExporter
from airtable_export.sql.sql_repository import SqlLiteRepository
from airtable_export.exporter.yaml_exporter import YamlExporter


@click.command()
@click.version_option()
@click.argument(
    "output_path",
    type=click.Path(file_okay=False, dir_okay=True, allow_dash=False),
    required=True,
)
@click.argument(
    "base_id",
    type=str,
    required=True,
)
@click.argument("tables", type=str, nargs=-1)
@click.option("--key", envvar="AIRTABLE_KEY", help="Airtable API key", required=True)
@click.option(
    "--http-read-timeout",
    help="Timeout (in seconds) for network read operations",
    type=int,
)
@click.option("--user-agent", help="User agent to use for requests")
@click.option("-v", "--verbose", is_flag=True, help="Verbose file_path")
@click.option("--json", is_flag=True, help="JSON format")
@click.option("--ndjson", is_flag=True, help="Newline delimited JSON format")
@click.option("--yaml", is_flag=True, help="YAML format (default)")
@click.option(
    "--sqlite",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    help="Export to this SQLite database",
)
def cli(
    output_path,
    base_id,
    tables,
    key,
    http_read_timeout,
    user_agent,
    verbose,
    json,
    ndjson,
    yaml,
    sqlite,
):
    # Export Airtable data to JSON/YAML/SQL-Lite file on disk
    file_path = pathlib.Path(output_path)
    file_path.mkdir(parents=True, exist_ok=True)
    airtable_client = AirtableClient(base_id, key, http_read_timeout, user_agent)
    logger = ClickLogger()
    if not json and not ndjson and not yaml and not sqlite:
        yaml = True
    if sqlite:
        path_sqlite = file_path / sqlite
        sql_repository = SqlLiteRepository(path_sqlite)
    for table_name in tables:
        records = airtable_client.get_all_records(table_name)
        if sqlite:
            sql_repository.write(table_name, records)
        filenames = []
        if json:
            json_file = JsonExporter.generate_file(file_path, records, table_name)
            filenames.append(json_file)
        if ndjson:
            nd_json_file = NDJsonExporter.generate_file(file_path, records, table_name)
            filenames.append(nd_json_file)
        if yaml:
            yaml_file = YamlExporter.generate_file(file_path, records, table_name)
            filenames.append(yaml_file)
        if verbose:
            logger.log(records, filenames)


yaml_.add_representer(str, YamlExporter.presenter)
