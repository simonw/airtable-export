import click
import httpx
from httpx import HTTPError
import json as json_
import pathlib
from urllib.parse import quote, urlencode
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
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("--json", is_flag=True, help="JSON format")
@click.option("--ndjson", is_flag=True, help="Newline delimited JSON format")
def cli(output_path, base_id, tables, key, verbose, json, ndjson):
    "Export Airtable data to YAML file on disk"
    output = pathlib.Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    for table in tables:
        ext = "yml"
        if json:
            ext = "json"
        elif ndjson:
            ext = "ndjson"
        filename = "{}.{}".format(table, ext)
        records = []
        try:
            for record in all_records(base_id, table, key):
                r = {
                    **{"airtable_id": record["id"]},
                    **record["fields"],
                    **{"airtable_createdTime": record["createdTime"]},
                }
                records.append(r)
        except HTTPError as exc:
            raise click.ClickException(exc)
        if json:
            dumped = json_.dumps(records, sort_keys=True, indent=4)
        elif ndjson:
            dumped = "\n".join(json_.dumps(r, sort_keys=True) for r in records)
        else:
            dumped = yaml.dump(records, sort_keys=True)
        (output / filename).write_text(dumped, "utf-8")
        if verbose:
            click.echo(
                "Wrote {} record{} to {}".format(
                    len(records), "" if len(records) == 1 else "s", (output / filename)
                ),
                err=True,
            )


def all_records(base_id, table, api_key, sleep=0.2):
    first = True
    offset = None
    while first or offset:
        first = False
        url = "https://api.airtable.com/v0/{}/{}".format(base_id, quote(table))
        if offset:
            url += "?" + urlencode({"offset": offset})
        response = httpx.get(
            url, headers={"Authorization": "Bearer {}".format(api_key)}
        )
        response.raise_for_status()
        data = response.json()
        offset = data.get("offset")
        yield from data["records"]
        if offset and sleep:
            time.sleep(sleep)


def str_representer(dumper, data):
    try:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    except TypeError:
        pass
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_representer)
