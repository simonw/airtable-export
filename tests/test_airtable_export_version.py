from click.testing import CliRunner
from airtable_export import cli


class TestAirtableExportVersion:

    def test_version(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli.cli, ["--version"])
            assert 0 == result.exit_code
            assert result.output.startswith("cli, version ")
