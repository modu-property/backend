from typing import Optional
from manticore.manticore_client import SearchClientInterface
from modu_property.utils.validator import validate_data
from real_estate.containers.container import ServiceContainer
from real_estate.dto.get_real_estate_dto import (
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.serializers import (
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
)
from dependency_injector.wiring import inject, Provide

from real_estate.services.set_real_estates import SetRealEstates


class SearchRealEstates:
    def __init__(
        self,
        search_client: SearchClientInterface = Provide[
            ServiceContainer.search_real_estates
        ],
    ) -> None:
        self.search_client: SearchClientInterface = search_client

    def search(self, dto: GetRealEstatesOnSearchDto, index: str = "") -> list:
        real_estates = []
        query = {"query_string": f"@* *{dto.keyword}*"}

        self._set_region_count_limit(dto, index)

        hits = self.search_client.search(index=index, query=query, limit=dto.limit)

        for hit in hits:
            real_estate_info = hit["_source"]
            real_estate_id = int(hit["_id"])
            real_estate_info["id"] = real_estate_id
            real_estates.append(real_estate_info)

        return real_estates

    def _set_region_count_limit(self, dto, index):
        dto.limit = 3


class GetRealEstatesOnSearchService:
    @inject
    def __init__(
        self,
        set_real_estate: SetRealEstates = Provide[
            ServiceContainer.set_real_estate_real_estates
        ],
        set_region: SetRealEstates = Provide[ServiceContainer.set_real_estate_regions],
    ) -> None:
        self.set_real_estate = set_real_estate
        self.set_region = set_region
        self.search_real_estate = SearchRealEstates()

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto) -> ServiceResultDto:
        result: dict[str, list] = {}

        regions = self.search_real_estate.search(dto=dto, index="region_index")

        is_regions_set: Optional[bool] = self.set_region.set(
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

        is_real_estates_set: Optional[bool] = self.set_real_estate.set(
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
