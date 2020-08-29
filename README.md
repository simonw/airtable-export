# airtable-to-yaml

[![PyPI](https://img.shields.io/pypi/v/airtable-to-yaml.svg)](https://pypi.org/project/airtable-to-yaml/)
[![Changelog](https://img.shields.io/github/v/release/simonw/airtable-to-yaml?include_prereleases&label=changelog)](https://github.com/simonw/airtable-to-yaml/releases)
[![Tests](https://github.com/simonw/airtable-to-yaml/workflows/Test/badge.svg)](https://github.com/simonw/airtable-to-yaml/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/airtable-to-yaml/blob/master/LICENSE)

Export Airtable data to YAML files on disk

## Installation

Install this tool using `pip`:

    $ pip install airtable-to-yaml

## Usage

You will need to know the following information:

- Your Airtable base ID - this is a string starting with `app...`
- Your Airtable API key - this is a string starting with `key...`
- The names of each of the tables that you wish to export

You can export all of your data to a folder called `export/` by running the following:

    airtable-to-yaml export base_id table1 table2 --key=key

This example would create two files: `export/table1.yml` and `export/table2.yml`.

Rather than passing the API key using the `--key` option you can set it as an environment variable called `AIRTABLE_KEY`.

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd airtable-to-yaml
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
