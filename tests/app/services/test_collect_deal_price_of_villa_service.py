import pytest
from property.services.collect_deal_price_of_villa_service import (
    CollectDealPriceOfVillaService,
)


@pytest.mark.django_db
class TestCollectDealPriceOfVillaService:
    def test_collect_deal_price_of_villa(mock_collect_deal_price_of_villa):
        result = CollectDealPriceOfVillaService().execute()

        assert result == True
