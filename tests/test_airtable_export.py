from click.testing import CliRunner
from airtable_export import cli
import httpx
import textwrap


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli.cli, ["--version"])
        assert 0 == result.exit_code
        assert result.output.startswith("cli, version ")


def test_airtable_export(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 200
    m.get.return_value.json.return_value = AIRTABLE_RESPONSE
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.cli, [".", "appZOGvNJPXCQ205F", "tablename", "-v", "--key", "x"]
        )
        assert 0 == result.exit_code
        assert "Wrote 1 record to tablename.yml" == result.output.strip()
        actual = open("tablename.yml").read()
        expected = textwrap.dedent(
            """
          - airtable_id: rec1
            name: This is the name
            address: |-
              Address line 1
              Address line 2
            size: 441
            true_or_false: true
            airtable_createdTime: '2020-04-18T18:50:27.000Z'
        """
        )
        assert expected.strip() == actual.strip()


def test_airtable_export_error(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 401
    m.get.return_value.raise_for_status.side_effect = httpx.HTTPError(
        "Unauthorized", request=None
    )
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
                "size": 441,
                "true_or_false": True,
            },
            "createdTime": "2020-04-18T18:50:27.000Z",
        }
    ]
}
