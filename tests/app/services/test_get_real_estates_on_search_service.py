import pytest

from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.services.get_real_estates_on_search_service import (
    GetRealEstatesOnSearchService,
)


def test_when_search_and_update_regions_fail_then_get_real_estates_raises_exception(
    mocker,
):
    mocker.patch(
        "real_estate.services.get_real_estates_on_search_service.GetRealEstatesOnSearchService._search_and_update_real_estates",
        return_value=False,
    )
    with pytest.raises(Exception) as exception_info:
        dto = GetRealEstatesOnSearchDto(
            deal_type=DealTypesForDBEnum.DEAL.value,
            keyword="강남",
            limit=10,
        )
        GetRealEstatesOnSearchService().get_real_estates(dto=dto)

    assert (
        exception_info.value.args[0]
        == "_search_and_update_real_estates region failed"
    )
