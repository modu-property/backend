from datetime import date
import pytest
from real_estate.management.commands.collect_deal_price_of_real_estate_command import (
    Command,
)
from real_estate.models import Deal, RealEstate
from django.contrib.gis.geos.point import Point
from tests.conftests.real_estate_conftest import insert_regional_codes


@pytest.mark.skip
@pytest.mark.django_db(transaction=True)
def test_collect_deal_price_of_estate_command(insert_regional_codes):
    insert_regional_codes()

    # Command().handle()
    # Command().handle(sido="서울특별시")

    real_estates = RealEstate.objects.prefetch_related("deals").all()

    for real_estate in real_estates:
        real_estate: RealEstate = real_estate
        deal: Deal = real_estate.deal.get()

        assert real_estate.id == deal.real_estate.id

        assert isinstance(real_estate.name, str)
        assert isinstance(real_estate.build_year, int)
        assert isinstance(real_estate.regional_code, str)
        assert isinstance(real_estate.lot_number, str)
        assert (
            isinstance(real_estate.road_name_address, str)
            or real_estate.road_name_address is None
        )
        assert isinstance(real_estate.latitude, str)
        assert isinstance(real_estate.longitude, str)
        assert isinstance(real_estate.point, Point)

        assert isinstance(deal.deal_price, int)
        assert isinstance(deal.deal_type, str) or deal.deal_type is None
        assert isinstance(deal.deal_year, int)
        assert isinstance(deal.land_area, str)
        assert isinstance(deal.deal_month, int)
        assert isinstance(deal.deal_day, int)
        assert isinstance(deal.area_for_exclusive_use, str)
        assert isinstance(deal.floor, str)
        assert isinstance(deal.is_deal_canceled, bool)
        assert (
            isinstance(deal.deal_canceled_date, date) or deal.deal_canceled_date is None
        )
        assert isinstance(deal.area_for_exclusive_use_pyung, str)
        assert isinstance(deal.area_for_exclusive_use_price_per_pyung, str)
        assert isinstance(deal.type, str)
