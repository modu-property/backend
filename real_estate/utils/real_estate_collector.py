import json
import logging
from typing import Union

import requests
import xmltodict

logger = logging.getLogger("django")


class RealEstateCollector:
    def collect_deal_price_of_real_estate(
        self, url: str, params: dict
    ) -> Union[list[dict], bool]:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            content: dict = xmltodict.parse(response.content, encoding="utf-8")

            # Convert dictionary to JSON
            json_response: json = json.loads(json.dumps(content, indent=4))

            return json_response["response"]["body"]["items"]["item"]

        logger.error(response.status_code, "get_deal_price_of_real_estate 수집 실패")

        return False
