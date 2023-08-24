class TestData:
    ANY_BASE_ID = "any-base-id"
    ANY_TABLE_NAME = "any-table-name"
    ANY_AIRTABLE_KEY = "any-key"

    FORMATS = [
        (
            "yaml",
            "yml",
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
        "ndjson",
        r"""
{"address": "Address line 1\nAddress line 2", "airtable_createdTime": "2020-04-18T18:50:27.000Z", "airtable_id": "rec1", "name": "This is the name", "size": 441, "true_or_false": true, "weird name: what is this?": "hello"}
{"address": "Address line 1\nAddress line 2", "airtable_createdTime": "2020-04-18T18:58:27.000Z", "airtable_id": "rec2", "name": "This is the name 2", "size": 442, "true_or_false": false, "weird name: what is this?": "there"}
       """,
        ),
    ]
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

