from typing import Optional, Dict

from real_estate.containers.service_container import (
    ServiceContainer,
)
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from dependency_injector.wiring import inject, Provide

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

        self._search_and_update_real_estates(
            dto,
            "region_index",
            "_search_and_update_real_estates regions failed",
            result,
            self.set_region.update_result_with_data,
        )

        self._search_and_update_real_estates(
            dto,
            "real_estate",
            "_search_and_update_real_estates real_estates failed",
            result,
            self.set_real_estate.update_result_with_data,
        )

        if not result:
            raise NotFoundException(message="not found")

        return result

    def _search_and_update_real_estates(
        self, dto, index, message, result, update_method
    ):
        is_updated = self._search_and_update(
            dto,
            result,
            update_method,
            index,
        )
        if is_updated is False:
            raise SearchAndUpdateRealEstatesException(message=message)

    def _search_and_update(
        self, dto, result, update_method, index: str
    ) -> bool:
        real_estates = self.search_real_estates.search(dto=dto, index=index)
        is_updated: Optional[bool] = update_method(
            result=result, data=real_estates
        )
        return is_updated
