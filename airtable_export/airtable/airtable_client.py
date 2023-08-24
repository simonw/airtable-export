import time
from urllib.parse import quote, urlencode


class AirtableClient:
    def __init__(self, base_id, api_key, http_read_timeout, user_agent=None):
        self.base_id = base_id
        self.api_key = api_key
        self.http_read_timeout = http_read_timeout
        self.user_agent = user_agent

    def get_all_records(self, table_name):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if self.user_agent is not None:
            headers["user-agent"] = self.user_agent

        if self.http_read_timeout:
            timeout = httpx.Timeout(5, read=self.http_read_timeout)
            client = httpx.Client(timeout=timeout)
        else:
            client = httpx

        first = True
        offset = None
        while first or offset:
            first = False
            url = f"https://api.airtable.com/v0/{self.base_id}/{quote(table_name)}"
            if offset:
                url += "?" + urlencode({"offset": offset})
            response = client.get(url, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            offset = json_data.get("offset")
            yield from json_data["records"]
            if offset:
                time.sleep(0.2)
