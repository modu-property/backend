from typing import Dict

from real_estate.containers.service_container import (
    ServiceContainer,
)
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from dependency_injector.wiring import inject, Provide

from real_estate.enum.real_estate_enum import SearchLimitEnum
from real_estate.exceptions import (
    SearchAndUpdateRealEstatesException,
    NotFoundException,
)
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

    def get_real_estates(self, dto: GetRealEstatesOnSearchDto) -> Dict:
        result: Dict[str, list] = {}

        dto.limit = SearchLimitEnum.REGION.value
        self._process_search_and_update(
            dto,
            result,
            index="region_index",
            update_method=self.set_region.update_result_with_data,
        )

        dto.limit = (
            dto.real_estate_search_limit
            if dto.real_estate_search_limit
            else SearchLimitEnum.REAL_ESTATES.value
        )
        self._process_search_and_update(
            dto,
            result,
            index="real_estate",
            update_method=self.set_real_estate.update_result_with_data,
        )

        if not result:
            raise NotFoundException(message="not found")

        return result

    def _process_search_and_update(self, dto, result, index, update_method):
        real_estates = self._search(
            dto=dto,
            index=index,
        )
        is_updated = self._update_result(
            result=result,
            real_estates=real_estates,
            update_method=update_method,
        )
        if is_updated is False:
            raise SearchAndUpdateRealEstatesException(
                message=f"_update_result failed dto : {dto}, result : {result}, index : {index}, update_method : {update_method}"
            )

    def _search(self, dto, index):
        return self.search_real_estates.search(dto=dto, index=index)

    @staticmethod
    def _update_result(result, real_estates, update_method) -> bool:
        return update_method(result=result, data=real_estates)
