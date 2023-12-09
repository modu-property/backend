import json
from typing import Union

import requests
import xmltodict


class RealEstateCollector:
    def collect_deal_price_of_real_estate(
        self, params: dict
    ) -> Union[list[dict], bool]:
        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            content: dict = xmltodict.parse(response.content, encoding="utf-8")

            # Convert dictionary to JSON
            json_response: json = json.loads(json.dumps(content, indent=4))

            return json_response["response"]["body"]["items"]["item"]

        print(response.status_code, "get_deal_price_of_real_estate 수집 실패")

        return False
