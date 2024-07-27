from typing import List, Union, Optional
import PublicDataReader as pdr
from dependency_injector.wiring import inject, Provide

from pandas import DataFrame
from modu_property.utils.loggers import logger

from real_estate.containers.utils.address_converter_container import (
    AddressConverterContainer,
)

from real_estate.models import Region
from real_estate.serializers import RegionSerializer
from real_estate.utils.address_converter_util import KakaoAddressConverterUtil


class AddressCollectorUtil:
    @inject
    def __init__(
        self,
        address_converter_util: KakaoAddressConverterUtil = Provide[
            AddressConverterContainer.address_converter
        ],
    ) -> None:
        self.address_converter_util: KakaoAddressConverterUtil = (
            address_converter_util
        )

    def collect_region(self) -> Union[List[Region], bool]:
        """
        법정동 코드, 시도, 시군구, 읍면동 수집
        """
        table: DataFrame = pdr.code_bdong()
        return self.get_region_models(table=table)

    def get_region_models(self, table: DataFrame) -> List[Optional[Region]]:
        region_list = []
        for _, row in table.iterrows():
            logger.info(f"get_region_models row : {row}")
            if not row.get("말소일자"):
                regional_code = row.get("시군구코드", None)
                sido = row.get("시도명", None)
                sigungu = row.get("시군구명", None)
                ubmyundong = row.get("읍면동명", None)
                dongri = row.get("동리명", None)

                logger.info(row)

                query: str = f"{sido} {sigungu} {ubmyundong} {dongri}".strip()

                if not self.address_converter_util.convert_address(query=query):
                    continue

                address_info: Union[dict[str, str], dict, bool] = (
                    self.address_converter_util.get_address()
                )
                logger.info(address_info)

                if address_info is False:
                    continue

                region_list.append(
                    dict(
                        sido=sido,
                        regional_code=regional_code,
                        sigungu=sigungu,
                        ubmyundong=ubmyundong,
                        dongri=dongri,
                        latitude=address_info["latitude"],
                        longitude=address_info["longitude"],
                    )
                )

        serializer = RegionSerializer(data=region_list, many=True)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(e)
            return []

        return [Region(**data) for data in serializer.validated_data]
