import os
import pytest

from real_estate.enum.deal_enum import DealType
from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)
from tests.conftests.account_conftest import get_jwt
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
        url = os.getenv("DEAL_PRICE_OF_VILLA_API")
        type = DealType.DEAL.value

        result = CollectDealPriceOfRealEstateService(url=url, type=type).execute(
            dong_code="11110", deal_ymd="201211"
        )

        assert result == True
