from datetime import date
from typing import List
import pytest
from real_estate.management.commands.collect_deal_price_of_real_estate_command import (
    Command,
)
from real_estate.models import Deal, RealEstate
from django.contrib.gis.geos.point import Point


@pytest.mark.skip(reason="수집 오래걸려서 스킵함")
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_collect_deal_price_of_estate_command(insert_regional_codes):
    insert_regional_codes()

    Command().handle(sido="서울특별시", start_date="200601", end_date="200601")

    real_estates = RealEstate.objects.prefetch_related("deals").all()

    for real_estate in real_estates:
        real_estate: RealEstate = real_estate
        deals: List[Deal] = list(real_estate.deals.all())

        assert isinstance(real_estate.name, str)
        assert isinstance(real_estate.build_year, int)
        assert isinstance(real_estate.regional_code, str)
        assert isinstance(real_estate.lot_number, str)
        assert (
            isinstance(real_estate.road_name_address, str)
            or real_estate.road_name_address is None
        )
        assert isinstance(real_estate.address, str) or real_estate.address is None
        assert isinstance(real_estate.latitude, str)
        assert isinstance(real_estate.longitude, str)
        assert isinstance(real_estate.point, Point)

        for deal in deals:
            assert real_estate.id == deal.real_estate.id

            assert isinstance(deal.deal_price, int)
            assert isinstance(deal.brokerage_type, str) or deal.brokerage_type is None
            assert isinstance(deal.deal_year, int)
            assert isinstance(deal.land_area, str)
            assert isinstance(deal.deal_month, int)
            assert isinstance(deal.deal_day, int)
            assert isinstance(deal.area_for_exclusive_use, str)
            assert isinstance(deal.floor, str)
            assert isinstance(deal.is_deal_canceled, bool)
            assert (
                isinstance(deal.deal_canceled_date, date)
                or deal.deal_canceled_date is None
            )
            assert isinstance(deal.area_for_exclusive_use_pyung, str)
            assert isinstance(deal.area_for_exclusive_use_price_per_pyung, str)
            assert isinstance(deal.deal_type, str)
