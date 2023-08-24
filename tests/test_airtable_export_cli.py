from click.testing import CliRunner
from airtable_export import cli
from airtable_export.airtable.airtable_client import AirtableClient
import httpx
import pytest
import sqlite_utils

from resources.test_data import TestData


class TestAirtableExportCli:

    @pytest.fixture
    def mocked_httpx(self, mocker):
        m = mocker.patch.object(AirtableClient, "httpx")
        m.get.return_value = mocker.Mock()
        m.get.return_value.status_code = 200
        m.get.return_value.json.return_value = TestData.AIRTABLE_RESPONSE

    @pytest.mark.parametrize("flag,file_format,expected", TestData.FORMATS)
    def test_export(self, mocked_httpx, flag, file_format, expected):
        runner = CliRunner()
        table_name = TestData.ANY_TABLE_NAME
        file_directory = "/tmp/dump"
        with runner.isolated_filesystem():
            args = [
                file_directory,
                TestData.ANY_BASE_ID,
                TestData.ANY_TABLE_NAME,
                "-v",
                "--key",
                TestData.ANY_AIRTABLE_KEY,
                f"--{flag}",
            ]
            result = runner.invoke(
                cli.cli,
                args,
            )
            assert 0 == result.exit_code
            assert (f"Wrote 2 records to {table_name}.{file_format}" == result.output.strip())
            actual = open(f"{file_directory}/{table_name}.{file_format}").read()
            assert expected.strip() == actual.strip()

    @pytest.mark.parametrize("flag,file_format,expected", TestData.FORMATS)
    def test_export_to_yaml_json_and_ndjson_at_the_same_time(self, mocked_httpx, flag, file_format, expected):
        runner = CliRunner()
        table_name = TestData.ANY_TABLE_NAME
        file_directory = "/tmp/dump"
        with runner.isolated_filesystem():
            args = [
                file_directory,
                TestData.ANY_BASE_ID,
                TestData.ANY_TABLE_NAME,
                "-v",
                "--key",
                TestData.ANY_AIRTABLE_KEY,
                "--yaml",
                "--json",
                "--ndjson",
            ]
            result = runner.invoke(
                cli.cli,
                args,
            )
            assert 0 == result.exit_code, result.stdout
            assert (f"Wrote 2 records to {table_name}.json, {table_name}.ndjson, {table_name}.yml" == result.output.strip())
            actual = open(f"{file_directory}/{table_name}.{file_format}").read()
            assert expected.strip() == actual.strip()

    def test_export_to_sql_lite(self, mocked_httpx):
        runner = CliRunner()
        table_name = TestData.ANY_TABLE_NAME
        file_directory = "/tmp/dump"
        sql_filename = "test.db"
        with runner.isolated_filesystem():
            args = [
                file_directory,
                TestData.ANY_BASE_ID,
                table_name,
                "--key",
                TestData.ANY_AIRTABLE_KEY,
                "--sqlite",
                sql_filename,
            ]
            result = runner.invoke(cli.cli, args, catch_exceptions=False)
            assert 0 == result.exit_code, result.stdout
            db = sqlite_utils.Database(f"{file_directory}/{sql_filename}")
            assert db.table_names() == [table_name]
            assert list(db[table_name].rows) == [
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

    def test_export_to_yaml_when_no_flags_are_provided(self, mocked_httpx):
        runner = CliRunner()
        table_name = TestData.ANY_TABLE_NAME
        file_directory = "/tmp/dump"
        with runner.isolated_filesystem():
            args = [
                file_directory,
                TestData.ANY_BASE_ID,
                TestData.ANY_TABLE_NAME,
                "--key",
                TestData.ANY_AIRTABLE_KEY,
                "-v"
            ]
            result = runner.invoke(
                cli.cli,
                args,
            )
            assert 0 == result.exit_code
            assert (f"Wrote 2 records to {table_name}.yml" == result.output.strip())
            actual = open(f"{file_directory}/{table_name}.yml").read()
            assert actual

    def test_airtable_export_error(self, mocker):
        runner = CliRunner()
        table_name = TestData.ANY_TABLE_NAME
        with runner.isolated_filesystem():
            m = mocker.patch.object(AirtableClient, "httpx")
            m.get.return_value = mocker.Mock()
            m.get.return_value.status_code = 401
            m.get.return_value.raise_for_status.side_effect = httpx.HTTPError("Unauthorized")
            result = runner.invoke(
                cli.cli, [".", TestData.ANY_BASE_ID, table_name, "-v", "--key", TestData.ANY_AIRTABLE_KEY]
            )

            assert result.exit_code == 1
            assert result.stdout == "Error: Unauthorized\n"


