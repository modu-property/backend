from typing import Any, Optional, Union

from manticore.manticore_client import ManticoreClient

from modu_property.utils.loggers import logger
from modu_property.utils.validator import validate_data
from real_estate.dto.real_estate_dto import (
    GetRealEstateDto,
    GetRealEstatesOnMapDto,
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.models import RealEstate
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchResponseSerializer,
    GetRegionsOnSearchResponseSerializer,
)
from django.contrib.gis.geos import Point
from django.db.models import QuerySet


class GetRealEstateService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def execute(self, dto: GetRealEstateDto) -> ServiceResultDto:
        real_estate: Optional[RealEstate] = self.repository.get_real_estate(id=dto.id)

        if not real_estate:
            return ServiceResultDto(status_code=404)

        data: Any = validate_data(
            model=real_estate,
            serializer=GetRealEstateResponseSerializer,
        )
        if not data:
            return ServiceResultDto(
                message="GetRealEstateResponseSerializer 에러", status_code=400
            )
        return ServiceResultDto(data=data)


class GetRealEstatesOnSearchService:
    def __init__(self) -> None:
        self.manticoresearch_client = ManticoreClient()

    def execute(self, dto: GetRealEstatesOnSearchDto) -> ServiceResultDto:
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

    def execute(self, dto: GetRealEstatesOnMapDto) -> ServiceResultDto:
        distance_tolerance: int = self.get_distance_tolerance(dto=dto)
        center_point = Point(
            float(dto.latitude), float(dto.longitude), srid=4326
        )  # 위경도 받아서 지도의 중심으로 잡음

        real_estates: Union[
            QuerySet, bool
        ] = self.repository.get_real_estates_by_latitude_and_longitude(
            distance_tolerance=distance_tolerance, center_point=center_point
        )
        if real_estates:
            data: Union[dict, bool, Any] = validate_data(
                model=real_estates,
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
        return ServiceResultDto(status_code=404)

    def get_distance_tolerance(self, dto: GetRealEstatesOnMapDto):
        # TODO level은 임시로 정함, 바꿔야함, 1,2 정도의 레벨은 하나하나 보여주지 말고 뭉쳐서 개수만 표현해야할듯..
        zoom_levels: dict[int, int] = {
            1: 50 * 1000,
            2: 25 * 1000,
            3: 15 * 1000,
            4: 10 * 1000,
            5: 5 * 1000,
            6: 1 * 1000,
        }
        return zoom_levels.get(dto.zoom_level, 1)
