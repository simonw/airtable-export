import time
import httpx
import click

from httpx import HTTPError
from urllib.parse import quote, urlencode


class AirtableClient:
    def __init__(self, base_id, api_key, http_read_timeout, user_agent=None):
        self.base_id = base_id
        self.api_key = api_key
        self.http_read_timeout = http_read_timeout
        self.user_agent = user_agent
        if self.http_read_timeout:
            timeout = httpx.Timeout(5, read=self.http_read_timeout)
            self._httpx = httpx.Client(timeout=timeout)
        else:
            self._httpx = httpx

    @property
    def httpx(self):
        return self._httpx

    def get_all_records(self, table_name):
        try:
            table_records = self._get_all_records(table_name)
            records = []
            for record in table_records:
                record = {
                    **{"airtable_id": record["id"]},
                    **record["fields"],
                    **{"airtable_createdTime": record["createdTime"]},
                }
                records.append(record)
            return records
        except HTTPError as exception:
            raise click.ClickException(exception) from exception

    def _get_all_records(self, table_name):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if self.user_agent is not None:
            headers["user-agent"] = self.user_agent
        first = True
        offset = None
        while first or offset:
            first = False
            url = f"https://api.airtable.com/v0/{self.base_id}/{quote(table_name)}"
            if offset:
                url += "?" + urlencode({"offset": offset})
            response = self.httpx.get(url, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            offset = json_data.get("offset")
            yield from json_data["records"]
            if offset:
                time.sleep(0.2)
