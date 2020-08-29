from setuptools import setup
import os

VERSION = "0.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="airtable-export",
    description="Export Airtable data to files on disk",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/airtable-export",
    project_urls={
        "Issues": "https://github.com/simonw/airtable-export/issues",
        "CI": "https://github.com/simonw/airtable-export/actions",
        "Changelog": "https://github.com/simonw/airtable-export/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["airtable_export"],
    entry_points="""
        [console_scripts]
        airtable-export=airtable_export.cli:cli
    """,
    install_requires=["click", "PyYAML", "httpx"],
    extras_require={"test": ["pytest", "pytest-mock"]},
    tests_require=["airtable-export[test]"],
)
