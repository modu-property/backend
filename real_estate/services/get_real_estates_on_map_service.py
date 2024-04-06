from typing import Any, Union
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnMapDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import RealEstateZoomLevel, RegionZoomLevel
from real_estate.repository.real_estate_repository import RealEstateRepository
from django.db.models import QuerySet

from real_estate.serializers import (
    GetRealEstatesOnMapResponseSerializer,
    GetRegionsOnMapResponseSerializer,
)


class GetRealEstatesOnMapService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def get_real_estates(self, dto: GetRealEstatesOnMapDto) -> ServiceResultDto:
        if (
            RealEstateZoomLevel.MIN.value <= dto.zoom_level
            and dto.zoom_level <= RealEstateZoomLevel.MAX.value
        ):
            real_estates: Union[QuerySet, bool] = (
                self.repository.get_individual_real_estates(dto=dto)
            )

            if real_estates:
                data: Union[dict, bool, Any] = validate_data(
                    queryset=real_estates,
                    serializer=GetRealEstatesOnMapResponseSerializer,
                    many=True,
                )

                if data:
                    return ServiceResultDto(data=data)
                else:
                    return ServiceResultDto(
                        message="GetRealEstatesOnMapResponseSerializer 에러",
                        status_code=400,
                    )
        elif (
            RegionZoomLevel.DONGRI.value <= dto.zoom_level
            and dto.zoom_level <= RegionZoomLevel.SIDO.value
        ):
            """
            region 테이블의 위경도 내에 있고, 시군구동 단위 일치하는것들을 region_price랑 join해서 응답
            """
            region_prices: Union[QuerySet, bool] = self.repository.get_region_prices(
                dto=dto
            )

            if region_prices:
                _data = validate_data(
                    serializer=GetRegionsOnMapResponseSerializer,
                    queryset=region_prices,
                    many=True,
                )

                if _data:
                    return ServiceResultDto(data=_data)
                else:
                    return ServiceResultDto(
                        message="GetRegionsOnMapResponseSerializer 에러",
                        status_code=400,
                    )
        return ServiceResultDto(status_code=404)
