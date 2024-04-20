from datetime import datetime
import pytest
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.enum.real_estate_enum import RealEstateTypesForDBEnum
from real_estate.models import RegionPrice
from real_estate.repository.real_estate_repository import RealEstateRepository

from real_estate.services.collect_region_price_service import (
    CollectRegionPriceService,
)
from django.contrib.gis.geos import Point


@pytest.mark.django_db
class TestCollectRegionPriceService:
    def test_collect_region_price(
        self, create_real_estate, create_deal, create_region
    ):
        repository = RealEstateRepository()

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

        real_estate1 = create_real_estate(
            name="풍림팍사이드빌라",
            build_year=1996,
            regional_code="11110",
            lot_number="134-2",
            road_name_address="서울 종로구 자하문로 99-3",
            address="부산 해운대구 청운동 134-2",
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

        create_region()

        region = repository.get_region(sido="서울특별시")

        dto: CollectRegionPriceDto = CollectRegionPriceDto(
            region=region,
            deal_type=DealTypesForDBEnum.DEAL.value,
            deal_year=deal.deal_year,
            deal_month=deal.deal_month,
            is_deal_canceled=False,
        )

        region_price = CollectRegionPriceService().collect_region_price(dto=dto)

        assert isinstance(region_price, RegionPrice)

        region_prices = repository.get_region_prices()
        region_prices = list(region_prices)

        for region_price in list(region_prices):
            assert region_price.region_id == region.id
            assert (
                region_price.deal_date
                == datetime.strptime("2006-01-01", "%Y-%m-%d").date()
            )
            assert region_price.total_deal_price == 28000
            assert region_price.total_jeonse_price == 0
            assert region_price.total_deal_price_per_pyung == "1719.90"
            assert region_price.total_jeonse_price_per_pyung == "0"
            assert region_price.average_deal_price == "28000.00"
            assert region_price.average_jeonse_price == "0"
            assert region_price.average_deal_price_per_pyung == "1719.90"
            assert region_price.average_jeonse_price_per_pyung == "0"
            assert region_price.deal_count == 1
            assert region_price.jeonse_count == 0

    def test_collect_region_price_with_multiple_regions(
        self, create_real_estate, create_deal, create_region
    ):
        repository = RealEstateRepository()

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

        deal = create_deal(
            real_estate_id=real_estate1.id,
            deal_price=15000,
            brokerage_type=None,
            deal_year=2006,
            land_area="40.11",
            deal_month=1,
            deal_day=30,
            area_for_exclusive_use="40.32",
            floor=5,
            is_deal_canceled=False,
            deal_canceled_date=None,
            area_for_exclusive_use_pyung="13.56",
            area_for_exclusive_use_price_per_pyung="1106.19",
            deal_type=DealTypesForDBEnum.DEAL.value,
        )

        # 동 이름만 같은 부동산
        real_estate2 = create_real_estate(
            name="풍림팍사이드빌라",
            build_year=1996,
            regional_code="11110",
            lot_number="134-2",
            road_name_address="서울 종로구 자하문로 99-3",
            address="부산 해운대구 청운동 134-2",
            real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
            latitude="37.5848604533872",
            longitude="126.969812605749",
            point=Point(37.5848604533872, 126.969812605749),
        )

        deal = create_deal(
            real_estate_id=real_estate2.id,
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

        # 취소된 거래는 제외
        deal = create_deal(
            real_estate_id=real_estate1.id,
            deal_price=15000,
            brokerage_type=None,
            deal_year=2006,
            land_area="40.11",
            deal_month=1,
            deal_day=30,
            area_for_exclusive_use="40.32",
            floor=5,
            is_deal_canceled=True,
            deal_canceled_date=None,
            area_for_exclusive_use_pyung="13.56",
            area_for_exclusive_use_price_per_pyung="1106.19",
            deal_type=DealTypesForDBEnum.DEAL.value,
        )

        region = create_region(sigungu="종로구", ubmyundong="청운동")

        region = repository.get_region(
            sido=region.sido,
            sigungu=region.sigungu,
            ubmyundong=region.ubmyundong,
        )

        dto: CollectRegionPriceDto = CollectRegionPriceDto(
            region=region,
            deal_type=DealTypesForDBEnum.DEAL.value,
            deal_year=deal.deal_year,
            deal_month=deal.deal_month,
            is_deal_canceled=False,
        )

        region_price = CollectRegionPriceService().collect_region_price(dto=dto)

        assert isinstance(region_price, RegionPrice)

        region_prices = repository.get_region_prices()
        region_prices = list(region_prices)

        for region_price in list(region_prices):
            assert region_price.region_id == region.id
            assert (
                region_price.deal_date
                == datetime.strptime("2006-01-01", "%Y-%m-%d").date()
            )
            assert region_price.total_deal_price == 43000
            assert region_price.total_jeonse_price == 0
            assert region_price.total_deal_price_per_pyung == "2826.09"
            assert region_price.total_jeonse_price_per_pyung == "0"
            assert region_price.average_deal_price == "21500.00"
            assert region_price.average_jeonse_price == "0"
            assert region_price.average_deal_price_per_pyung == "1413.05"
            assert region_price.average_jeonse_price_per_pyung == "0"
            assert region_price.deal_count == 2
            assert region_price.jeonse_count == 0
