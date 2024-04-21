from typing import List, Union
import PublicDataReader as pdr
from dependency_injector.wiring import inject, Provide

from pandas.core.series import Series
from django.forms import model_to_dict
from pandas import DataFrame
from modu_property.utils.loggers import logger

from modu_property.utils.validator import validate_data

from real_estate.containers.utils.address_converter_container import (
    AddressConverterContainer,
)

from real_estate.models import Region
from real_estate.serializers import RegionSerializer
from real_estate.utils.address_converter import KakaoAddressConverter


class AddressCollector:
    @inject
    def __init__(
        self,
        address_converter: KakaoAddressConverter = Provide[
            AddressConverterContainer.address_converter
        ],
    ) -> None:
        self.address_converter: KakaoAddressConverter = address_converter

    def collect_region(self) -> Union[List[Region], bool]:
        """
        법정동 코드, 시도, 시군구, 읍면동 수집
        """
        table: DataFrame = pdr.code_bdong()

        region_models = []
        for _, row in table.iterrows():
            self.get_region_models(row=row, region_models=region_models)

        logger.info(f"region_models count {len(region_models)}")

        is_validated = validate_data(
            serializer=RegionSerializer,
            data=[model_to_dict(region) for region in region_models],
            many=True,
        )
        if not is_validated:
            return False

        return region_models

    def get_region_models(self, row: Series, region_models: List[Region]):
        if not row.get("말소일자"):
            regional_code = row.get("시군구코드", None)
            sido = row.get("시도명", None)
            sigungu = row.get("시군구명", None)
            ubmyundong = row.get("읍면동명", None)
            dongri = row.get("동리명", None)

            logger.info(row)

            query: str = f"{sido} {sigungu} {ubmyundong} {dongri}".strip()

            if not self.address_converter.convert_address(query=query):
                return False

            address_info: Union[dict[str, str], dict, bool] = (
                self.address_converter.get_address()
            )
            logger.info(address_info)

            if address_info is False:
                return None

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
