import pytest
from rest_framework import status

from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.services.get_real_estates_on_search_service import (
    GetRealEstatesOnSearchService,
)


def test_when_search_and_update_regions_fail_then_get_real_estates_raises_exception(
    mocker,
):
    mocker.patch(
        "real_estate.services.get_real_estates_on_search_service.GetRealEstatesOnSearchService._update_result",
        return_value=False,
    )
    with pytest.raises(Exception) as exception_info:
        dto = GetRealEstatesOnSearchDto(
            deal_type=DealTypesForDBEnum.DEAL.value,
            keyword="강남",
            real_estate_search_limit=10,
        )
        GetRealEstatesOnSearchService().get_real_estates(dto=dto)

    assert "_update_result failed" in exception_info.value.args[0]
    assert exception_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_when_search_and_update_real_estates_fail_then_get_real_estates_raises_exception(
    mocker,
):
    mocker.patch(
        "real_estate.services.get_real_estates_on_search_service.GetRealEstatesOnSearchService._update_result",
        side_effect=[True, False],
    )
    with pytest.raises(Exception) as exception_info:
        dto = GetRealEstatesOnSearchDto(
            deal_type=DealTypesForDBEnum.DEAL.value,
            keyword="강남",
            real_estate_search_limit=10,
        )
        GetRealEstatesOnSearchService().get_real_estates(dto=dto)

    assert "_update_result failed" in exception_info.value.args[0]
    assert exception_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_when_no_result_then_raises_exception(
    mocker,
):
    mocker.patch(
        "real_estate.services.get_real_estates_on_search_service.GetRealEstatesOnSearchService._update_result",
        side_effect=[None, None],
    )
    with pytest.raises(Exception) as exception_info:
        dto = GetRealEstatesOnSearchDto(
            deal_type=DealTypesForDBEnum.DEAL.value,
            keyword="강남",
            real_estate_search_limit=10,
        )
        GetRealEstatesOnSearchService().get_real_estates(dto=dto)

    assert exception_info.value.args[0] == "not found"
    assert exception_info.value.status_code == status.HTTP_404_NOT_FOUND
