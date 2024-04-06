from typing import Any
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


class GetRealEstatesOnSearchService:
    def __init__(self) -> None:
        self.manticoresearch_client = ManticoreClient()

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto) -> ServiceResultDto:
        result: dict[str, list] = {}

        regions: list = self._search_real_estates(dto=dto, index="region_index")
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

        real_estates: list = self._search_real_estates(dto=dto, index="real_estate")
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

    def _search_real_estates(
        self, dto: GetRealEstatesOnSearchDto, index: str = ""
    ) -> list:
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
        if index == "region_index":
            dto.limit = 3
