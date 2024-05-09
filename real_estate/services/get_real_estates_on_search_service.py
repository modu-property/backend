from typing import Optional

from modu_property.utils.validator import validate_data

from real_estate.containers.service_container import (
    ServiceContainer,
)
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.serializers import (
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
)
from dependency_injector.wiring import inject, Provide

from real_estate.services.search_real_estates_service import (
    SearchRealEstatesService,
)
from real_estate.services.set_real_estates_service import SetRealEstatesService


class GetRealEstatesOnSearchService:
    @inject
    def __init__(
        self,
        set_real_estate: SetRealEstatesService = Provide[
            ServiceContainer.set_real_estate_real_estates
        ],
        set_region: SetRealEstatesService = Provide[
            ServiceContainer.set_real_estate_regions
        ],
        search_real_estates=Provide[ServiceContainer.search_real_estates],
    ) -> None:
        self.set_real_estate: SetRealEstatesService = set_real_estate
        self.set_region: SetRealEstatesService = set_region
        self.search_real_estates: SearchRealEstatesService = search_real_estates

    def get_real_estates(
        self, dto: GetRealEstatesOnSearchDto
    ) -> ServiceResultDto:
        result: dict[str, list] = {}

        regions = self.search_real_estates.search(dto=dto, index="region_index")

        is_regions_updated: Optional[bool] = (
            self.set_region.update_result_with_data(result=result, data=regions)
        )
        if is_regions_updated is False:
            return ServiceResultDto(
                message="GetRegionsOnSearchResponseSerializer 에러",
                status_code=400,
            )

        real_estates: list = self.search_real_estates.search(
            dto=dto, index="real_estates"
        )

        is_real_estates_updated: Optional[bool] = (
            self.set_real_estate.update_result_with_data(
                result=result,
                data=real_estates,
            )
        )
        if is_real_estates_updated is False:
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
