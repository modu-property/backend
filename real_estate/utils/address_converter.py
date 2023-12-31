import os
from typing import Union
import requests

from modu_property.utils.loggers import logger


class AddressConverter:
    def convert_address(self, dong: str, lot_number: str) -> Union[dict, bool]:
        headers = {"Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}"}
        params = {"query": f"{dong} {lot_number}"}
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            logger.error("카카오 주소 변환 실패")
            return False

        documents = response.json()["documents"]

        if not documents:
            logger.error("documents 없음")
            return False

        try:
            document = documents[0]
            road_name_address = (
                document["road_address"]["address_name"]
                if document.get("road_address")
                else None
            )
            latitude = document["y"]
            longitude = document["x"]

            return {
                "road_name_address": road_name_address,
                "latitude": latitude,
                "longitude": longitude,
            }
        except Exception as e:
            logger.error(f"주소 변환 실패 e : {e}")
            return {}
