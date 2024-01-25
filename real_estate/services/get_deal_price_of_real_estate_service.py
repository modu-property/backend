from typing import Any, Union
from manticore.manticore_client import ManticoreClient

from modu_property.utils.loggers import logger
from modu_property.utils.validator import validate_model
from real_estate.dto.real_estate_dto import (
    GetRealEstateDto,
    GetRealEstatesOnMapDto,
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchResponseSerializer,
)
from django.contrib.gis.geos import Point


class GetRealEstateService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def execute(self, dto: GetRealEstateDto):
        real_estate = self.repository.get_real_estate(id=dto.id)

        try:
            serializer = GetRealEstateResponseSerializer(real_estate)
            return serializer.data
        except Exception as e:
            logger.error(f"GetRealEstateService e : {e}")
            return {}


class GetRealEstatesOnSearchService:
    def __init__(self) -> None:
        self.manticoresearch_client = ManticoreClient()

    def execute(self, dto: GetRealEstatesOnSearchDto) -> ServiceResultDto:
        real_estates = self.get_real_estates(dto=dto)
        if real_estates:
            serializer = GetRealEstatesOnSearchResponseSerializer(
                data=list(real_estates), many=True
            )
            if serializer.is_valid():
                return ServiceResultDto(data=serializer.data)
            else:
                logger.error(f"GetRealEstatesOnSearchService e : {serializer.errors}")
                return ServiceResultDto(
                    message="GetRealEstatesOnSearchResponseSerializer 에러",
                    status_code=400,
                )
        return ServiceResultDto(status_code=404)

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto) -> list:
        real_estates = []
        index = "real_estate"
        query = {"query_string": f"@* *{dto.keyword}*"}
        hits = self.manticoresearch_client.search(index=index, query=query)

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
            list[dict], bool
        ] = self.repository.get_real_estates_by_latitude_and_longitude(
            distance_tolerance=distance_tolerance, center_point=center_point
        )
        if real_estates:
            data: Union[dict, bool, Any] = validate_model(
                data=real_estates,
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
            1: 10 * 10,
            2: 8 * 8,
            3: 6 * 6,
            4: 4 * 4,
            5: 2 * 2,
            6: 1 * 1,
        }
        # zoom_levels.
        return zoom_levels.get(dto.zoom_level, 1)
