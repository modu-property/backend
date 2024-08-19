import os
from time import sleep
from typing import Dict, Optional, Union
import requests

from requests import Response
from requests.adapters import HTTPAdapter

from modu_property.utils.loggers import logger


class KakaoAddressConverterUtil:
    def __init__(self) -> None:
        self.address_info = {}

    def convert_address(self, query: str) -> Optional[bool]:
        sleep(0.00001)
        address_info: Union[Dict, bool] = self._get_address_info(query=query)
        if not address_info:
            return False

        try:
            road_name_address: str = self._get_road_name_address(address_info)
            address: str = self._get_address(address_info)
            latitude: str = address_info["y"]
            longitude: str = address_info["x"]

            if not road_name_address:
                raise Exception(f"도로명 주소 없음 {address_info.__dict__}")

            self.address_info = {
                "road_name_address": road_name_address,
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
            }
            return True
        except Exception as e:
            logger.error(f"주소 변환 실패 e : {e}")
            return False

    def get_address(self) -> Union[dict[str, str], dict, bool]:
        return self.address_info

    def _get_address(self, document):
        return (
            document["address"]["address_name"]
            if document.get("address")
            else ""
        )

    def _get_road_name_address(self, document):
        return (
            document["road_address"]["address_name"]
            if document.get("road_address")
            else ""
        )

    def _get_address_info(self, query: str):
        with requests.Session() as session:
            self._set_max_retries(session=session)

            response: Response = self._request_kakao_address(
                query=query, session=session
            )

            if response.status_code != 200:
                logger.error(
                    f"카카오 주소 변환 실패 response : {response.__dict__}"
                )
                return False

            try:
                return response.json()["documents"][0]
            except Exception as e:
                logger.error(f"카카오 주소 변환 실패 e : {e}")
                return False

    def _request_kakao_address(self, query, session):
        headers = {"Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}"}
        params = {"query": query}
        logger.info(f"query : {query}")
        response = session.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers=headers,
            params=params,
        )

        return response

    def _set_max_retries(self, session):
        adapter = HTTPAdapter(max_retries=1)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
