import pytest
from django.urls import reverse

from real_estate.enum.deal_enum import BrokerageTypesEnum, DealTypesForDBEnum
from real_estate.enum.real_estate_enum import RealEstateTypesForDBEnum
from django.contrib.gis.geos import Point


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_real_estate(client, get_jwt, create_real_estate, create_deal):
    real_estate1 = create_real_estate(
        name="테스트빌라 1",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 서초구 반포동 739",
        road_name_address="서울특별시 서초구 사평대로53길 22 (반포동)",
        address="서울특별시 서초구 반포동 739",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5054",
        longitude="127.0216",
        point=Point(37.5054, 127.0216),
    )

    create_deal(
        real_estate_id=real_estate1.id,
        deal_price=10000,
        brokerage_type=BrokerageTypesEnum.DIRECT.value,
        deal_year=2023,
        land_area=100,
        deal_month=3,
        deal_day=21,
        area_for_exclusive_use=80,
        floor=3,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="30.30",
        area_for_exclusive_use_price_per_pyung="330",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    create_deal(
        real_estate_id=real_estate1.id,
        deal_price=20000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2023,
        land_area=200,
        deal_month=12,
        deal_day=30,
        area_for_exclusive_use=150,
        floor=5,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    url = reverse("get-real-estate", kwargs={"id": real_estate1.id})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}

    response = client.get(url, **headers)
    assert response.status_code == 200

    real_estate = response.json()
    assert real_estate["id"] == real_estate1.id
    assert real_estate["name"] == real_estate1.name
    assert real_estate["build_year"] == real_estate1.build_year
    assert real_estate["regional_code"] == real_estate1.regional_code
    assert real_estate["lot_number"] == real_estate1.lot_number
    assert real_estate["road_name_address"] == real_estate1.road_name_address
    assert real_estate["real_estate_type"] == real_estate1.real_estate_type
    assert real_estate["latitude"] == real_estate1.latitude
    assert real_estate["longitude"] == real_estate1.longitude
