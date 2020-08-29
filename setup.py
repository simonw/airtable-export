from setuptools import setup
import os

VERSION = "0.1.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="airtable-to-yaml",
    description="Export Airtable data to YAML files on disk",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/airtable-to-yaml",
    project_urls={
        "Issues": "https://github.com/simonw/airtable-to-yaml/issues",
        "CI": "https://github.com/simonw/airtable-to-yaml/actions",
        "Changelog": "https://github.com/simonw/airtable-to-yaml/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["airtable_to_yaml"],
    entry_points="""
        [console_scripts]
        airtable-to-yaml=airtable_to_yaml.cli:cli
    """,
    install_requires=["click", "PyYAML", "httpx"],
    extras_require={"test": ["pytest", "pytest-mock"]},
    tests_require=["airtable-to-yaml[test]"],
)
