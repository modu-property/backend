import pytest

from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.deal_enum import DealType
from real_estate.models import RealEstate
from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)
from django.contrib.gis.geos import Point
from tests.conftests.real_estate_conftest import (
    mock_collect_deal_price_of_real_estate,
    create_real_estate,
    create_deal,
)


@pytest.mark.django_db
class TestCollectDealPriceOfRealEstateService:
    def test_collect_deal_price_of_villa(
        self,
        mocker,
        mock_collect_deal_price_of_real_estate,
        create_real_estate,
        create_deal,
    ):
        mocker.patch(
            "real_estate.utils.real_estate_collector.RealEstateCollector.collect_deal_price_of_real_estate",
            return_value=mock_collect_deal_price_of_real_estate,
        )

        real_estate1 = create_real_estate(
            name="풍림팍사이드빌라",
            build_year=1997,
            regional_code="11110",
            lot_number="134-2",
            road_name_address="서울 종로구 자하문로 99-3",
            latitude="37.5848604533872",
            longitude="126.969812605749",
            point=Point(37.5848604533872, 126.969812605749),
        )

        create_deal(
            real_estate_id=real_estate1.id,
            deal_price=28000,
            deal_type=None,
            deal_year=2020,
            land_area="37.902",
            deal_month=1,
            deal_day=20,
            area_for_exclusive_use="53.83",
            floor=2,
            is_deal_canceled=False,
            deal_canceled_date=None,
            area_for_exclusive_use_pyung="16.28",
            area_for_exclusive_use_price_per_pyung="1719.90",
            type=DealType.DEAL.value,
        )

        dto = CollectDealPriceOfRealEstateDto(
            property_type="연립다세대",
            trade_type=DealType.DEAL.value,
            regional_code="11110",
            year_month="202001",
        )

        result = CollectDealPriceOfRealEstateService().execute(dto=dto)

        assert result == True

        real_estates = (
            RealEstate.objects.prefetch_related("deal")
            .filter(
                regional_code=dto.regional_code,
                deal__deal_year=int(dto.year_month[:4]),
                deal__deal_month=int(dto.year_month[4:]),
                deal__type=dto.trade_type,
                # deal__deal_type=None,
            )
            .all()
        )

        for real_estate in real_estates:
            assert real_estate1.name != real_estate
