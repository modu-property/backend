import os
from typing import List, Union
import PublicDataReader as pdr

from PublicDataReader import TransactionPrice
from pandas import DataFrame
from modu_property.utils.loggers import logger

from real_estate.models import Region
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.utils.address_converter import KakaoAddressConverter


class AddressCollector:
    def __init__(self) -> None:
        self.service_key = os.getenv("SERVICE_KEY")
        self.api = TransactionPrice(self.service_key)
        self.real_estate_repository = RealEstateRepository()
        self.kakao_address_converter = KakaoAddressConverter()

    def collect_regional_info(self) -> Union[List[Region], bool]:
        """
        법정동 코드, 시도, 시군구, 읍면동 수집
        """
        table: DataFrame = pdr.code_bdong()

        region_models = []
        for _, row in table.iterrows():
            if not row.get("말소일자"):
                regional_code = row.get("시군구코드", None)
                sido = row.get("시도명", None)
                sigungu = row.get("시군구명", None)
                ubmyundong = row.get("읍면동명", None)
                dongri = row.get("동리명", None)

                logger.info(row)

                query: str = f"{sido} {sigungu} {ubmyundong} {dongri}".strip()

                address_info: Union[
                    dict[str, str], dict, bool
                ] = self.kakao_address_converter.convert_address(query=query)
                logger.info(address_info)

                if not address_info:
                    continue

                region = Region(
                    sido=sido,
                    regional_code=regional_code,
                    sigungu=sigungu,
                    ubmyundong=ubmyundong,
                    dongri=dongri,
                    latitude=address_info["latitude"],
                    longitude=address_info["longitude"],
                )
                logger.info(f"region : {region}")

                region_models.append(region)

        logger.info(f"region_models count {len(region_models)}")
        result: Union[
            List[Region], bool
        ] = self.real_estate_repository.bulk_create_regions(region_models=region_models)

        return result
