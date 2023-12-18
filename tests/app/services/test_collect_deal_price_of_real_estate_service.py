import pytest

from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)
from tests.conftests.real_estate_conftest import mock_collect_deal_price_of_real_estate


@pytest.mark.django_db
class TestCollectDealPriceOfRealEstateService:
    def test_collect_deal_price_of_villa(
        self, mocker, mock_collect_deal_price_of_real_estate
    ):
        mocker.patch(
            "real_estate.utils.real_estate_collector.RealEstateCollector.collect_deal_price_of_real_estate",
            return_value=mock_collect_deal_price_of_real_estate,
        )

        dto = CollectDealPriceOfRealEstateDto(
            property_type="연립다세대",
            trade_type="매매",
            regional_code="11110",
            year_month="202001",
        )

        result = CollectDealPriceOfRealEstateService().execute(dto=dto)

        assert result == True
