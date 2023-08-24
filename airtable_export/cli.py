import click
import httpx
from httpx import HTTPError
import json
import pathlib
from urllib.parse import quote, urlencode
import sqlite_utils
import time
import yaml


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
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
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
    is_json,
    is_ndjson,
    is_yaml,
    sqlite,
):
    # Export Airtable data to JSON/YAML/SQL-Lite file on disk
    output = pathlib.Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    if any(x for x in [is_json, is_ndjson, is_yaml, sqlite]):
        is_yaml = True
    if sqlite:
        sqlite_filepath = output / sqlite
        db = sqlite_utils.Database(sqlite_filepath)
    for table_name in tables:
        records = []
        try:
            db_records = []
            table_records = get_all_table_records(base_id, table_name, key, http_read_timeout, user_agent)
            for record in table_records:
                record = {
                    **{"airtable_id": record["id"]},
                    **record["fields"],
                    **{"airtable_createdTime": record["createdTime"]},
                }
                records.append(record)
                db_records.append(record)
                if sqlite and len(db_records) == 100:
                    write_batch(db, table_name, db_records)
                    db_records = []
        except HTTPError as exc:
            raise click.ClickException(exc)
        write_batch(db, table_name, db_records)
        filenames = []
        if is_json:
            json_file = generate_json_file(output, records, table_name)
            filenames.append(json_file)
        if is_ndjson:
            nd_json_file = generate_nd_json_file(output, records, table_name)
            filenames.append(nd_json_file)
        if is_yaml:
            yaml_file = generate_yaml_file(output, records, table_name)
            filenames.append(yaml_file)
        if verbose:
            filenames_seperated_by_comma = ", ".join(filenames)
            number_of_records = len(records)
            log_records(number_of_records, filenames_seperated_by_comma)


def write_batch(db, table_name, records):
    db[table_name].insert_all(records, pk="airtable_id", replace=True, alter=True)


def log_records(filenames, number_of_records):
    human_friendly_records = "record" if number_of_records == 1 else "records"
    log_message = f"Wrote {number_of_records} {human_friendly_records} to {filenames}"
    click.echo(log_message, err=True)


def generate_yaml_file(output, records, table_name):
    filename = f"{table_name}.yml"
    dumped = yaml.dump(records, sort_keys=True)
    yaml_filepath = output / filename
    yaml_filepath.write_text(dumped, "utf-8")
    return yaml_filepath


def generate_nd_json_file(output, records, table_name):
    filename = f"{table_name}.ndjson"
    dumped = "\n".join(json.dumps(r, sort_keys=True) for r in records)
    ndjson_filepath = output / filename
    ndjson_filepath.write_text(dumped, "utf-8")
    return ndjson_filepath


def generate_json_file(output, records, table_name):
    filename = f"{table_name}.json"
    dumped = json.dumps(records, sort_keys=True, indent=4)
    json_filepath = output / filename
    json_filepath.write_text(dumped, "utf-8")
    return json_filepath


def get_all_table_records(base_id, table, api_key, http_read_timeout, user_agent=None):
    headers = {"Authorization": f"Bearer {api_key}"}
    if user_agent is not None:
        headers["user-agent"] = user_agent

    if http_read_timeout:
        timeout = httpx.Timeout(5, read=http_read_timeout)
        client = httpx.Client(timeout=timeout)
    else:
        client = httpx

    first = True
    offset = None
    while first or offset:
        first = False
        url = f"https://api.airtable.com/v0/{base_id}/{quote(table)}"
        if offset:
            url += "?" + urlencode({"offset": offset})
        response = client.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        offset = json_data.get("offset")
        yield from json_data["records"]
        if offset:
            time.sleep(0.2)


def str_representer(dumper, data):
    try:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    except TypeError:
        pass
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_representer)
