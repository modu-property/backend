import pytest
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.enum.real_estate_enum import RealEstateTypesForDBEnum
from real_estate.management.commands.collect_region_price_command import (
    Command,
)
from real_estate.models import RegionPrice

from real_estate.repository.real_estate_repository import RealEstateRepository
from django.contrib.gis.geos import Point


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_collect_region_price_command(create_real_estate, create_deal, create_region):
    real_estate1 = create_real_estate(
        name="풍림팍사이드빌라",
        build_year=1996,
        regional_code="11110",
        lot_number="134-2",
        road_name_address="서울 종로구 자하문로 99-3",
        address="서울 종로구 청운동 134-2",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5848604533872",
        longitude="126.969812605749",
        point=Point(37.5848604533872, 126.969812605749),
    )

    deal = create_deal(
        real_estate_id=real_estate1.id,
        deal_price=28000,
        brokerage_type=None,
        deal_year=2006,
        land_area="37.902",
        deal_month=1,
        deal_day=20,
        area_for_exclusive_use="53.83",
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="16.28",
        area_for_exclusive_use_price_per_pyung="1719.90",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    real_estate2 = create_real_estate(
        name="제외될 부동산",
        build_year=1996,
        regional_code="11110",
        lot_number="134-2",
        road_name_address="부산 해운대구",
        address="부산 해운대구",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5848604533872",
        longitude="126.969812605749",
        point=Point(37.5848604533872, 126.969812605749),
    )

    deal = create_deal(
        real_estate_id=real_estate2.id,
        deal_price=10000,
        brokerage_type=None,
        deal_year=2006,
        land_area="37.902",
        deal_month=1,
        deal_day=20,
        area_for_exclusive_use="53.83",
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="16.28",
        area_for_exclusive_use_price_per_pyung="1719.90",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    create_region()
    Command().handle(sido="서울특별시", start_date="200601", end_date="200601")

    repository = RealEstateRepository()
    region_prices = repository.get_region_prices()

    for region_price in region_prices:
        region_price: RegionPrice = region_price

        assert isinstance(region_price.total_deal_price, int)
        assert isinstance(region_price.total_jeonse_price, int)
        assert isinstance(region_price.total_deal_price_per_pyung, str)
        assert isinstance(region_price.total_jeonse_price_per_pyung, str)
        assert isinstance(region_price.average_deal_price, str)
        assert isinstance(region_price.average_jeonse_price, str)
        assert isinstance(region_price.average_deal_price_per_pyung, str)
        assert isinstance(region_price.average_jeonse_price_per_pyung, str)
        assert isinstance(region_price.deal_count, int)
        assert isinstance(region_price.jeonse_count, int)


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_when_collect_region_price_command_with_region_price_then_collect_from_last_deal_date(
    create_real_estate, create_deal, create_region, create_region_price
):
    real_estate1 = create_real_estate(
        name="풍림팍사이드빌라",
        build_year=1996,
        regional_code="11110",
        lot_number="134-2",
        road_name_address="서울 종로구 자하문로 99-3",
        address="서울 종로구 청운동 134-2",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5848604533872",
        longitude="126.969812605749",
        point=Point(37.5848604533872, 126.969812605749),
    )

    deal = create_deal(
        real_estate_id=real_estate1.id,
        deal_price=28000,
        brokerage_type=None,
        deal_year=2006,
        land_area="37.902",
        deal_month=1,
        deal_day=20,
        area_for_exclusive_use="53.83",
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="16.28",
        area_for_exclusive_use_price_per_pyung="1719.90",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    real_estate2 = create_real_estate(
        name="제외될 부동산",
        build_year=1996,
        regional_code="11110",
        lot_number="134-2",
        road_name_address="부산 해운대구",
        address="부산 해운대구",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5848604533872",
        longitude="126.969812605749",
        point=Point(37.5848604533872, 126.969812605749),
    )

    deal = create_deal(
        real_estate_id=real_estate2.id,
        deal_price=10000,
        brokerage_type=None,
        deal_year=2006,
        land_area="37.902",
        deal_month=1,
        deal_day=20,
        area_for_exclusive_use="53.83",
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="16.28",
        area_for_exclusive_use_price_per_pyung="1719.90",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    region = create_region()
    create_region_price(region_id=region.id)
    Command().handle(sido="서울특별시")

    repository = RealEstateRepository()
    region_prices = repository.get_region_prices()

    for region_price in region_prices:
        region_price: RegionPrice = region_price

        assert isinstance(region_price.total_deal_price, int)
        assert isinstance(region_price.total_jeonse_price, int)
        assert isinstance(region_price.total_deal_price_per_pyung, str)
        assert isinstance(region_price.total_jeonse_price_per_pyung, str)
        assert isinstance(region_price.average_deal_price, str)
        assert isinstance(region_price.average_jeonse_price, str)
        assert isinstance(region_price.average_deal_price_per_pyung, str)
        assert isinstance(region_price.average_jeonse_price_per_pyung, str)
        assert isinstance(region_price.deal_count, int)
        assert isinstance(region_price.jeonse_count, int)
