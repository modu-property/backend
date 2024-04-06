from typing import Any, Optional, Union

from manticore.manticore_client import ManticoreClient

from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import (
    GetRealEstateDto,
    GetRealEstatesOnMapDto,
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import RealEstateZoomLevel, RegionZoomLevel
from real_estate.models import RealEstate
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchResponseSerializer,
    GetRegionsOnMapResponseSerializer,
    GetRegionsOnSearchResponseSerializer,
)
from django.db.models import QuerySet


class GetRealEstateService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def get_real_estate(self, dto: GetRealEstateDto) -> ServiceResultDto:
        real_estate: Optional[RealEstate] = self.repository.get_real_estate(id=dto.id)

        if not real_estate:
            return ServiceResultDto(status_code=404)

        data: Any = validate_data(
            serializer=GetRealEstateResponseSerializer,
            queryset=real_estate,
        )
        if not data:
            return ServiceResultDto(
                message="GetRealEstateResponseSerializer 에러", status_code=400
            )
        return ServiceResultDto(data=data)


class GetRealEstatesOnSearchService:
    def __init__(self) -> None:
        self.manticoresearch_client = ManticoreClient()

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto) -> ServiceResultDto:
        result: dict[str, list] = {}

        regions: list = self.get_real_estates(dto=dto, index="region_index")
        if regions:
            data: Any = validate_data(
                data=list(regions),
                serializer=GetRegionsOnSearchResponseSerializer,
                many=True,
            )
            if not data:
                return ServiceResultDto(
                    message="GetRegionsOnSearchResponseSerializer 에러",
                    status_code=400,
                )

            result["regions"] = list(regions)

        real_estates: list = self.get_real_estates(dto=dto, index="real_estate")
        if real_estates:
            data: Any = validate_data(
                data=list(real_estates),
                serializer=GetRealEstatesOnSearchResponseSerializer,
                many=True,
            )
            if not data:
                return ServiceResultDto(
                    message="GetRealEstatesOnSearchResponseSerializer 에러",
                    status_code=400,
                )
            result["real_estates"] = list(real_estates)

        if real_estates or regions:
            data = validate_data(
                data=result,
                serializer=GetRealEstatesAndRegionsOnSearchResponseSerializer,
            )
            if not data:
                return ServiceResultDto(
                    message="GetRealEstatesAndRegionsOnSearchResponseSerializer 에러",
                    status_code=400,
                )

            return ServiceResultDto(data=result)
        return ServiceResultDto(status_code=404)

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto, index: str = "") -> list:
        real_estates = []
        query = {"query_string": f"@* *{dto.keyword}*"}

        if index == "region_index":
            dto.limit = 3

        hits = self.manticoresearch_client.search(
            index=index, query=query, limit=dto.limit
        )

        for hit in hits:
            real_estate_info = hit["_source"]
            real_estate_id = int(hit["_id"])
            real_estate_info["id"] = real_estate_id
            real_estates.append(real_estate_info)

        return real_estates


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
