from click.testing import CliRunner
from airtable_export import cli
import httpx
import pytest
import sqlite_utils

FORMATS = [
    (
        "yaml",
        """
- address: |-
    Address line 1
    Address line 2
  airtable_createdTime: '2020-04-18T18:50:27.000Z'
  airtable_id: rec1
  name: This is the name
  size: 441
  true_or_false: true
  'weird name: what is this?': hello
- address: |-
    Address line 1
    Address line 2
  airtable_createdTime: '2020-04-18T18:58:27.000Z'
  airtable_id: rec2
  name: This is the name 2
  size: 442
  true_or_false: false
  'weird name: what is this?': there
       """,
    ),
    (
        "json",
        r"""
[
    {
        "address": "Address line 1\nAddress line 2",
        "airtable_createdTime": "2020-04-18T18:50:27.000Z",
        "airtable_id": "rec1",
        "name": "This is the name",
        "size": 441,
        "true_or_false": true,
        "weird name: what is this?": "hello"
    },
    {
        "address": "Address line 1\nAddress line 2",
        "airtable_createdTime": "2020-04-18T18:58:27.000Z",
        "airtable_id": "rec2",
        "name": "This is the name 2",
        "size": 442,
        "true_or_false": false,
        "weird name: what is this?": "there"
    }
]
       """,
    ),
    (
        "ndjson",
        r"""
{"address": "Address line 1\nAddress line 2", "airtable_createdTime": "2020-04-18T18:50:27.000Z", "airtable_id": "rec1", "name": "This is the name", "size": 441, "true_or_false": true, "weird name: what is this?": "hello"}
{"address": "Address line 1\nAddress line 2", "airtable_createdTime": "2020-04-18T18:58:27.000Z", "airtable_id": "rec2", "name": "This is the name 2", "size": 442, "true_or_false": false, "weird name: what is this?": "there"}
       """,
    ),
]


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli.cli, ["--version"])
        assert 0 == result.exit_code
        assert result.output.startswith("cli, version ")


@pytest.fixture
def mocked(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 200
    m.get.return_value.json.return_value = AIRTABLE_RESPONSE


@pytest.mark.parametrize("format,expected", FORMATS)
def test_airtable_export(mocked, format, expected):
    runner = CliRunner()
    with runner.isolated_filesystem():
        args = [
            ".",
            "appZOGvNJPXCQ205F",
            "tablename",
            "-v",
            "--key",
            "x",
            "--{}".format(format),
        ]
        result = runner.invoke(
            cli.cli,
            args,
        )
        assert 0 == result.exit_code
        assert (
            "Wrote 2 records to tablename.{}".format(
                "yml" if format == "yaml" else format
            )
            == result.output.strip()
        )
        actual = open(
            "tablename.{}".format("yml" if format == "yaml" else format)
        ).read()
        assert expected.strip() == actual.strip()


def test_all_three_formats_at_once(mocked):
    runner = CliRunner()
    with runner.isolated_filesystem():
        args = [
            ".",
            "appZOGvNJPXCQ205F",
            "tablename",
            "-v",
            "--key",
            "x",
            "--yaml",
            "--json",
            "--ndjson",
        ]
        result = runner.invoke(
            cli.cli,
            args,
        )
        assert 0 == result.exit_code, result.stdout
        assert (
            "Wrote 2 records to tablename.json, tablename.ndjson, tablename.yml"
            == result.output.strip()
        )
        for format, expected in FORMATS:
            actual = open(
                "tablename.{}".format("yml" if format == "yaml" else format)
            ).read()
            assert expected.strip() == actual.strip()


def test_airtable_sqlite(mocked):
    runner = CliRunner()
    with runner.isolated_filesystem():
        args = [
            ".",
            "appZOGvNJPXCQ205F",
            "tablename",
            "--key",
            "x",
            "--sqlite",
            "test.db",
        ]
        result = runner.invoke(cli.cli, args, catch_exceptions=False)
        assert 0 == result.exit_code, result.stdout
        db = sqlite_utils.Database("test.db")
        assert db.table_names() == ["tablename"]
        assert list(db["tablename"].rows) == [
            {
                "airtable_id": "rec1",
                "name": "This is the name",
                "address": "Address line 1\nAddress line 2",
                "weird name: what is this?": "hello",
                "size": 441,
                "true_or_false": 1,
                "airtable_createdTime": "2020-04-18T18:50:27.000Z",
            },
            {
                "airtable_id": "rec2",
                "name": "This is the name 2",
                "address": "Address line 1\nAddress line 2",
                "weird name: what is this?": "there",
                "size": 442,
                "true_or_false": 0,
                "airtable_createdTime": "2020-04-18T18:58:27.000Z",
            },
        ]


def test_airtable_export_error(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 401
    m.get.return_value.raise_for_status.side_effect = httpx.HTTPError("Unauthorized")
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.cli, [".", "appZOGvNJPXCQ205F", "tablename", "-v", "--key", "x"]
        )
        assert result.exit_code == 1
        assert result.stdout == "Error: Unauthorized\n"


AIRTABLE_RESPONSE = {
    "records": [
        {
            "id": "rec1",
            "fields": {
                "name": "This is the name",
                "address": "Address line 1\nAddress line 2",
                "weird name: what is this?": "hello",
                "size": 441,
                "true_or_false": True,
            },
            "createdTime": "2020-04-18T18:50:27.000Z",
        },
        {
            "id": "rec2",
            "fields": {
                "name": "This is the name 2",
                "address": "Address line 1\nAddress line 2",
                "weird name: what is this?": "there",
                "size": 442,
                "true_or_false": False,
            },
            "createdTime": "2020-04-18T18:58:27.000Z",
        },
    ]
}
