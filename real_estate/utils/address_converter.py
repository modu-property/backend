import os
from time import sleep
from typing import Union
import requests
from requests.adapters import HTTPAdapter

from modu_property.utils.loggers import logger


class KakaoAddressConverter:
    def convert_address(self, query: str) -> Union[dict[str, str], dict, bool]:
        sleep(0.00001)
        response = None
        with requests.Session() as session:
            adapter = HTTPAdapter(max_retries=1)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            headers = {"Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}"}
            params = {"query": query}
            logger.info(f"query : {query}")
            response = session.get(
                "https://dapi.kakao.com/v2/local/search/address.json",
                headers=headers,
                params=params,
            )

            if response.status_code != 200:
                logger.error(f"카카오 주소 변환 실패 response : {response.__dict__}")
                return False

        documents = response.json()["documents"]

        if not documents:
            return False

        try:
            document = documents[0]
            road_name_address: str = (
                document["road_address"]["address_name"]
                if document.get("road_address")
                else ""
            )
            address: str = (
                document["address"]["address_name"] if document.get("address") else ""
            )
            latitude: str = document["y"]
            longitude: str = document["x"]

            return {
                "road_name_address": road_name_address,
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
            }
        except Exception as e:
            logger.error(f"주소 변환 실패 e : {e}")
            return {}
