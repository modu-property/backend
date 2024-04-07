from typing import Any, Dict, Optional, Union
from manticore.manticore_client import ManticoreClient
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import (
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.serializers import (
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
    GetRealEstatesOnSearchResponseSerializer,
    GetRegionsOnSearchResponseSerializer,
)


class SetRealEstate:
    def __init__(self, serializer, key) -> None:
        self.serializer: Union[
            GetRealEstatesOnSearchResponseSerializer,
            GetRegionsOnSearchResponseSerializer,
        ] = serializer
        self.key = key

    def _set(
        self,
        result: Dict,
        data: list,
    ):
        if not data:
            return False

        _data: Any = validate_data(
            data=list(data),
            serializer=self.serializer,
            many=True,
        )
        if not _data:
            return False

        result[self.key] = list(data)


class SearchRealEstates:
    def __init__(self) -> None:
        self.manticoresearch_client = ManticoreClient()

    def search(self, dto: GetRealEstatesOnSearchDto, index: str = "") -> list:
        real_estates = []
        query = {"query_string": f"@* *{dto.keyword}*"}

        self._set_region_count_limit(dto, index)

        hits = self.manticoresearch_client.search(
            index=index, query=query, limit=dto.limit
        )

        for hit in hits:
            real_estate_info = hit["_source"]
            real_estate_id = int(hit["_id"])
            real_estate_info["id"] = real_estate_id
            real_estates.append(real_estate_info)

        return real_estates

    def _set_region_count_limit(self, dto, index):
        dto.limit = 3


class GetRealEstatesOnSearchService:
    def __init__(self) -> None:
        self.manticoresearch_client = ManticoreClient()
        self.set_real_estate = SetRealEstate(
            serializer=GetRealEstatesOnSearchResponseSerializer, key="real_estates"
        )
        self.set_region = SetRealEstate(
            serializer=GetRegionsOnSearchResponseSerializer, key="regions"
        )
        self.search_real_estate = SearchRealEstates()

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto) -> ServiceResultDto:
        result: dict[str, list] = {}

        regions = self.search_real_estate.search(dto=dto, index="region_index")

        is_regions_set: Optional[bool] = self.set_region._set(
            result=result, data=regions
        )
        if is_regions_set is False:
            return ServiceResultDto(
                message="GetRegionsOnSearchResponseSerializer 에러",
                status_code=400,
            )

        real_estates: list = self.search_real_estate.search(
            dto=dto, index="real_estates"
        )

        is_real_estates_set: Optional[bool] = self.set_region._set(
            result=result,
            data=real_estates,
        )
        if is_real_estates_set is False:
            return ServiceResultDto(
                message="GetRealEstatesOnSearchResponseSerializer 에러",
                status_code=400,
            )

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
