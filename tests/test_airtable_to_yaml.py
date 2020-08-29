from click.testing import CliRunner
from airtable_to_yaml import cli
import textwrap


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli.cli, ["--version"])
        assert 0 == result.exit_code
        assert result.output.startswith("cli, version ")


def test_airtable_to_yaml(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 200
    m.get.return_value.json.return_value = AIRTABLE_RESPONSE
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli.cli, [".", "appZOGvNJPXCQ205F", "tablename", "-v", "--key", "x"])
        assert 0 == result.exit_code
        assert "Wrote 1 record to tablename.yml" == result.output.strip()
        actual = open('tablename.yml').read()
        expected = textwrap.dedent("""
          - airtable_id: rec1
            name: This is the name
            address: |-
              Address line 1
              Address line 2
            size: 441
            true_or_false: true
            airtable_createdTime: '2020-04-18T18:50:27.000Z'
        """)
        assert expected.strip() == actual.strip()


AIRTABLE_RESPONSE = {
    "records": [{
        "id": "rec1",
        "fields": {
            "name": "This is the name",
            "address": "Address line 1\nAddress line 2",
            "size": 441,
            "true_or_false": True,
        },
        "createdTime": "2020-04-18T18:50:27.000Z"
    }]
}
