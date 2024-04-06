import pytest

from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.enum.real_estate_enum import (
    RealEstateTypesForDBEnum,
    RealEstateTypesForQueryEnum,
)
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)
from django.contrib.gis.geos import Point


@pytest.mark.django_db
class TestCollectDealPriceOfRealEstateService:
    def test_collect_deal_price_of_villa(
        self,
        mocker,
        mock_collect_deal_price_of_real_estate,
        create_real_estate,
        create_deal,
    ):
        """
        풍림팍사이드빌라를 미리 DB에 생성하고
        mock_collect_deal_price_of_real_estate로 수집 목킹해서 3개 빌라를 반환함
        풍림팍사이드빌라가 이미 DB에 있어서 제외하고 2개 빌라 저장함
        """
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
            address="서울특별시 종로구 청운동 134-2",
            real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
            latitude="37.5848604533872",
            longitude="126.969812605749",
            point=Point(37.5848604533872, 126.969812605749),
        )

        create_deal(
            real_estate_id=real_estate1.id,
            deal_price=28000,
            brokerage_type=None,
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
            deal_type=DealTypesForDBEnum.DEAL.value,
        )

        dto = CollectDealPriceOfRealEstateDto(
            real_estate_type=RealEstateTypesForQueryEnum.MULTI_UNIT_HOUSE.value,
            deal_type=DealTypesForDBEnum.DEAL.value,
            regional_code="11110",
            year_month="202001",
        )

        result = (
            CollectDealPriceOfRealEstateService().collect_deal_price_of_real_estate(
                dto=dto
            )
        )

        assert result == True

        real_estates = RealEstateRepository().get_real_estates()

        assert len(real_estates) == 3
