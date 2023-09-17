from click.testing import CliRunner
from airtable_export import cli
import pathlib
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
def mock_table(httpx_mock):
    httpx_mock.add_response(
        url="https://api.airtable.com/v0/appZOGvNJPXCQ205F/tablename",
        json=AIRTABLE_RESPONSE,
    )


@pytest.fixture
def mock_table_list(httpx_mock):
    httpx_mock.add_response(
        url="https://api.airtable.com/v0/meta/bases/appZOGvNJPXCQ205F/tables",
        json={"tables": [{"id": "tbl123", "name": "tablename"}]},
    )


@pytest.mark.parametrize("format,expected", FORMATS)
@pytest.mark.parametrize(
    "extra_arguments", [["tablename"], [], ["tablename", "--schema"]]
)
def test_airtable_export(mock_table, httpx_mock, format, expected, extra_arguments):
    if not extra_arguments or "--schema" in extra_arguments:
        httpx_mock.add_response(
            url="https://api.airtable.com/v0/meta/bases/appZOGvNJPXCQ205F/tables",
            json={"tables": [{"id": "tbl123", "name": "tablename"}]},
        )
    runner = CliRunner()
    with runner.isolated_filesystem():
        args = (
            [
                ".",
                "appZOGvNJPXCQ205F",
            ]
            + extra_arguments
            + [
                "-v",
                "--key",
                "x",
                "--{}".format(format),
            ]
        )
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
        if not extra_arguments or "--schema" in extra_arguments:
            # Check schema was saved
            assert (pathlib.Path(".") / "_schema.json").exists()
            assert open("_schema.json").read()[0] == "{"
        else:
            assert not (pathlib.Path(".") / "_schema.json").exists()


def test_all_three_formats_at_once(mock_table):
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


def test_airtable_sqlite(mock_table):
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


def test_airtable_export_error(httpx_mock):
    httpx_mock.add_response(status_code=401)
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.cli, [".", "appZOGvNJPXCQ205F", "tablename", "-v", "--key", "x"]
        )
        assert result.exit_code == 1
        assert "401 Unauthorized" in result.output


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
