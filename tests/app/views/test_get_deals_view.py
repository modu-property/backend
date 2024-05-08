from urllib.parse import urlencode

import pytest
from django.contrib.gis.geos import Point
from django.test import Client
from django.urls import reverse

from real_estate.enum.deal_enum import BrokerageTypesEnum, DealTypesForDBEnum
from real_estate.enum.real_estate_enum import RealEstateTypesForDBEnum


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.parametrize(
    "title, deal_create_count, page, expected_deal_count, expected_current_page, expected_total_pages",
    [
        ("when deal count is 0, page is None then return 0", 0, None, 0, 1, 1),
        ("when deal count is 0, page is 1 then return 0", 0, 1, 0, 1, 1),
        (
            "when deal count is 11, page is None then return 10",
            11,
            None,
            10,
            1,
            2,
        ),
        ("when deal count is 12, page is 2 then return 2", 12, 2, 2, 2, 2),
        ("when deal count is 25, page is 2 then return 10", 25, 2, 10, 2, 3),
        ("when deal count is 25, page is 3 then return 5", 25, 3, 5, 3, 3),
    ],
)
def test_when_get_deals_then_return_deals(
    title,
    deal_create_count,
    page,
    expected_deal_count,
    expected_current_page,
    expected_total_pages,
    client: Client,
    get_jwt,
    create_real_estate,
    create_deal,
):
    real_estate = create_real_estate(
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

    year = 2024

    for i in range(deal_create_count):
        create_deal(
            real_estate_id=real_estate.id,
            deal_price=10000,
            brokerage_type=BrokerageTypesEnum.DIRECT.value,
            deal_year=year - i,
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

    another_real_estate = create_real_estate(
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
        real_estate_id=another_real_estate.id,
        deal_price=10000,
        brokerage_type=BrokerageTypesEnum.DIRECT.value,
        deal_year=year,
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

    url = reverse(
        "get-deals",
        kwargs={
            "id": real_estate.id,
            "deal_type": DealTypesForDBEnum.DEAL.value,
        },
    )

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}

    query_params = None
    if page:
        query_params = urlencode({"page": page})
        url = f"{url}?{query_params}"

    response = client.get(path=url, **headers, content_type="application/json")

    assert response.status_code == 200

    response_json = response.json()

    if deal_create_count == 0:
        response_json == []
    else:
        deals = response_json.get("results")
        current_page = response_json.get("current_page")
        total_pages = response_json.get("total_pages")
        assert len(deals) == expected_deal_count
        assert current_page == expected_current_page
        assert total_pages == expected_total_pages
