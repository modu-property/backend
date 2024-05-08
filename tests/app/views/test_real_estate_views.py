from django.http import JsonResponse
from django.urls import reverse
import pytest
from real_estate.enum.deal_enum import BrokerageTypesEnum, DealTypesForDBEnum
from real_estate.enum.real_estate_enum import (
    RealEstateTypesForDBEnum,
    RealEstateZoomLevelEnum,
    RegionZoomLevelEnum,
)
from django.contrib.gis.geos import Point
from datetime import datetime


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_real_estates_with_latitude_longitude_zoom_level_view(
    client, get_jwt, create_real_estate, create_deal
):
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
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
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
        deal_price=10000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2023,
        land_area=100,
        deal_month=4,
        deal_day=30,
        area_for_exclusive_use=80,
        floor=3,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="30.30",
        area_for_exclusive_use_price_per_pyung="330",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    real_estate2 = create_real_estate(
        name="OAK 빌",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 서초구 반포동 734-32 반포엠",
        road_name_address="서울특별시 서초구 사평대로53길 30 (반포동)",
        address="서울특별시 서초구 반포동 734-32 반포엠",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5056",
        longitude="127.0215",
        point=Point(37.5056, 127.0215),
    )

    create_deal(
        real_estate_id=real_estate2.id,
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

    real_estate3 = create_real_estate(
        name="봉은사로 빌라",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 강남구 논현동 175-19",
        road_name_address="서울특별시 강남구 봉은사로25길 34 (논현동)",
        address="서울특별시 강남구 논현동 175-19",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5094",
        longitude="127.0321",
        point=Point(37.5094, 127.0321),
    )

    create_deal(
        real_estate_id=real_estate3.id,
        deal_price=30000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2022,
        land_area=150,
        deal_month=1,
        deal_day=1,
        area_for_exclusive_use=130,
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    real_estate4 = create_real_estate(
        name="지산로얄빌라",
        build_year=1990,
        regional_code="21070",
        lot_number="부산광역시 남구 대연동 1724-1",
        road_name_address="부산광역시 남구 유엔로157번나길 48 (대연동, 지산로얄빌라)",
        address="부산광역시 남구 대연동 1724-1",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="35.133",
        longitude="129.0959",
        point=Point(35.133, 129.0959),
    )

    create_deal(
        real_estate_id=real_estate4.id,
        deal_price=30000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2022,
        land_area=150,
        deal_month=1,
        deal_day=1,
        area_for_exclusive_use=130,
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    url = reverse("get-real-estates-on-map", kwargs={"deal_type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "latitude": 37.5054,
        "longitude": 127.0216,
        "zoom_level": RealEstateZoomLevelEnum.DEFAULT.value,
        "keyword": "",
        "sw_lat": 37.5053,
        "sw_lng": 127.0215,
        "ne_lat": 37.5055,
        "ne_lng": 127.0217,
    }

    response: JsonResponse = client.get(url, data=query_params, **headers)
    assert response.status_code == 200

    data = response.json()
    real_estates = data.get("data")
    for real_estate in real_estates:
        assert "name" in real_estate
        assert "lot_number" in real_estate
        assert "address" in real_estate
        assert "road_name_address" in real_estate
        assert "build_year" in real_estate
        assert "deal_price" in real_estate
        assert "deal_date" in real_estate
        assert "real_estate_type" in real_estate
        assert "latitude" in real_estate
        assert "longitude" in real_estate
        assert "area_for_exclusive_use_pyung" in real_estate
        assert "area_for_exclusive_use_price_per_pyung" in real_estate


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_real_estates_on_map_view(
    client, get_jwt, create_real_estate, create_deal
):
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
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
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
        deal_price=10000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2023,
        land_area=100,
        deal_month=4,
        deal_day=30,
        area_for_exclusive_use=80,
        floor=3,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="30.30",
        area_for_exclusive_use_price_per_pyung="330",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    real_estate2 = create_real_estate(
        name="OAK 빌",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 서초구 반포동 734-32 반포엠",
        road_name_address="서울특별시 서초구 사평대로53길 30 (반포동)",
        address="서울특별시 서초구 반포동 734-32 반포엠",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5056",
        longitude="127.0215",
        point=Point(37.5056, 127.0215),
    )

    create_deal(
        real_estate_id=real_estate2.id,
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

    real_estate3 = create_real_estate(
        name="봉은사로 빌라",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 강남구 논현동 175-19",
        road_name_address="서울특별시 강남구 봉은사로25길 34 (논현동)",
        address="서울특별시 강남구 논현동 175-19",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="37.5094",
        longitude="127.0321",
        point=Point(37.5094, 127.0321),
    )

    create_deal(
        real_estate_id=real_estate3.id,
        deal_price=30000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2022,
        land_area=150,
        deal_month=1,
        deal_day=1,
        area_for_exclusive_use=130,
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    real_estate4 = create_real_estate(
        name="지산로얄빌라",
        build_year=1990,
        regional_code="21070",
        lot_number="부산광역시 남구 IntegerField()gerField()1724-1",
        road_name_address="부산광역시 남구 유엔로157번나길 48 (대연동, 지산로얄빌라)",
        address="부산광역시 남구 대연동 1724-1",
        real_estate_type=RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
        latitude="35.133",
        longitude="129.0959",
        point=Point(35.133, 129.0959),
    )

    create_deal(
        real_estate_id=real_estate4.id,
        deal_price=30000,
        brokerage_type=BrokerageTypesEnum.BROKERAGE.value,
        deal_year=2022,
        land_area=150,
        deal_month=1,
        deal_day=1,
        area_for_exclusive_use=130,
        floor=2,
        is_deal_canceled=False,
        deal_canceled_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
        deal_type=DealTypesForDBEnum.DEAL.value,
    )

    url = reverse("get-real-estates-on-map", kwargs={"deal_type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "latitude": 37.5054,
        "longitude": 127.0216,
        "sw_lat": 37.5053,
        "sw_lng": 127.0215,
        "ne_lat": 37.5055,
        "ne_lng": 127.0217,
        "zoom_level": RealEstateZoomLevelEnum.DEFAULT.value,
        "keyword": "",
    }

    response: JsonResponse = client.get(url, data=query_params, **headers)
    assert response.status_code == 200

    data = response.json()
    real_estates = data.get("data")
    for real_estate in real_estates:
        assert "latitude" in real_estate
        assert "longitude" in real_estate
        assert "real_estate_type" in real_estate
        assert "deal_price" in real_estate
        assert "deal_date" in real_estate
        assert "area_for_exclusive_use_pyung" in real_estate
        assert "area_for_exclusive_use_price_per_pyung" in real_estate


@pytest.mark.parametrize(
    "title, zoom_level, expected_region",
    [
        (
            "zoom_level 6 then dongri",
            RegionZoomLevelEnum.DONGRI.value,
            "dongri",
        ),
        (
            "zoom_level 7 then ubmyundong",
            RegionZoomLevelEnum.UBMYUNDONG.value,
            "ubmyundong",
        ),
        (
            "zoom_level 8 then sigungu",
            RegionZoomLevelEnum.SIGUNGU.value,
            "sigungu",
        ),
        ("zoom_level 9 then sido", RegionZoomLevelEnum.SIDO.value, "sido"),
    ],
)
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_region_prices_on_map_view(
    title,
    zoom_level,
    expected_region,
    client,
    get_jwt,
    create_region,
    create_region_price,
):
    """
    zool_level에 따라 시군구동읍면리 단위로 평균 매매가, 평균 평당가 등 응답
    """
    # sido
    region_sido = create_region(
        sido="서울특별시",
        sigungu="",
        ubmyundong="",
        dongri="",
        latitude=37.5054,
        longitude=127.0216,
    )

    create_region_price(
        region_id=region_sido.id,
        total_deal_price=636300,
        total_jeonse_price=0,
        total_deal_price_per_pyung="32356.95",
        total_jeonse_price_per_pyung="0",
        average_deal_price="17675.00",
        average_jeonse_price="0",
        average_deal_price_per_pyung="898.81",
        average_jeonse_price_per_pyung="0",
        deal_count=36,
        jeonse_count=0,
        deal_date=datetime.strptime("2006-01-01", "%Y-%m-%d"),
    )

    # sigungu
    region_sigungu = create_region(
        sido="서울특별시",
        sigungu="서초구",
        ubmyundong="",
        dongri="",
        latitude=37.5054,
        longitude=127.0216,
    )

    create_region_price(
        region_id=region_sigungu.id,
        total_deal_price=636300,
        total_jeonse_price=0,
        total_deal_price_per_pyung="32356.95",
        total_jeonse_price_per_pyung="0",
        average_deal_price="17675.00",
        average_jeonse_price="0",
        average_deal_price_per_pyung="898.81",
        average_jeonse_price_per_pyung="0",
        deal_count=36,
        jeonse_count=0,
        deal_date=datetime.strptime("2006-01-01", "%Y-%m-%d"),
    )

    # ubmyundong
    region_ubmyundong = create_region(
        sido="서울특별시",
        sigungu="서초구",
        ubmyundong="논현동",
        dongri="",
        latitude=37.5054,
        longitude=127.0216,
    )

    create_region_price(
        region_id=region_ubmyundong.id,
        total_deal_price=636300,
        total_jeonse_price=0,
        total_deal_price_per_pyung="32356.95",
        total_jeonse_price_per_pyung="0",
        average_deal_price="17675.00",
        average_jeonse_price="0",
        average_deal_price_per_pyung="898.81",
        average_jeonse_price_per_pyung="0",
        deal_count=36,
        jeonse_count=0,
        deal_date=datetime.strptime("2006-01-01", "%Y-%m-%d"),
    )

    # dong
    region_dong = create_region(
        sido="서울특별시",
        sigungu="서초구",
        ubmyundong="논현동",
        dongri="논현동",
        latitude=37.5054,
        longitude=127.0216,
    )

    create_region_price(
        region_id=region_dong.id,
        total_deal_price=636300,
        total_jeonse_price=0,
        total_deal_price_per_pyung="32356.95",
        total_jeonse_price_per_pyung="0",
        average_deal_price="17675.00",
        average_jeonse_price="0",
        average_deal_price_per_pyung="898.81",
        average_jeonse_price_per_pyung="0",
        deal_count=36,
        jeonse_count=0,
        deal_date=datetime.strptime("2006-01-01", "%Y-%m-%d"),
    )

    url = reverse("get-real-estates-on-map", kwargs={"deal_type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "sw_lat": 37.5053,
        "sw_lng": 127.0215,
        "ne_lat": 37.5055,
        "ne_lng": 127.0217,
        "zoom_level": zoom_level,
        "keyword": "",
    }

    response: JsonResponse = client.get(url, data=query_params, **headers)
    assert response.status_code == 200

    data = response.json()
    region_prices = data.get("data")
    for region_price in region_prices:
        assert "total_deal_price" in region_price
        assert "total_jeonse_price" in region_price
        assert "total_deal_price_per_pyung" in region_price
        assert "total_jeonse_price_per_pyung" in region_price
        assert "average_deal_price" in region_price
        assert "average_jeonse_price" in region_price
        assert "average_deal_price_per_pyung" in region_price
        assert "average_jeonse_price_per_pyung" in region_price
        assert "deal_count" in region_price
        assert "jeonse_count" in region_price
        assert "deal_date" in region_price

        region = region_price["region"]

        if expected_region == "sido":
            assert region["sido"]
            assert region["sigungu"] == ""
            assert region["ubmyundong"] == ""
            assert region["dongri"] == ""
        elif expected_region == "sigungu":
            assert region["sido"]
            assert region["sigungu"]
            assert region["ubmyundong"] == ""
            assert region["dongri"] == ""
        elif expected_region == "ubmyundong":
            assert region["sido"]
            assert region["sigungu"]
            assert region["ubmyundong"]
            assert region["dongri"] == ""
        elif expected_region == "dongri":
            assert region["sido"]
            assert region["sigungu"]
            assert region["ubmyundong"]
            assert region["dongri"]

        assert "latitude" in region
        assert "longitude" in region


@pytest.mark.django_db(transaction=True, reset_sequences=True)
# @pytest.mark.skip()
def test_get_real_estates_with_keyword_view(client, get_jwt):
    """
    !!로컬 데이터 사라지므로 주의!!
    터미널에서 아래 명령어 실행
    SERVER_ENV=local python manage.py insert_real_estates_for_searching_command
    manticore container에서 indexing
    indexer --config /etc/manticoresearch/manticore.conf --all --rotate
    """
    url = reverse("get-real-estates-on-search", kwargs={"deal_type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "keyword": "강남",
    }

    response = client.get(url, data=query_params, **headers)
    assert response.status_code == 200
