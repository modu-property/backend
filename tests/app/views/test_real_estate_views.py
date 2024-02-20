from django.http import JsonResponse
from django.urls import reverse
import pytest
from real_estate.enum.deal_enum import BrokerageTypesEnum, DealTypesForDBEnum
from real_estate.enum.real_estate_enum import RealEstateTypesForDBEnum
from django.contrib.gis.geos import Point
from datetime import datetime


@pytest.mark.django_db(transaction=True)
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
        "zoom_level": 6,
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
        assert "latitude" in real_estate
        assert "longitude" in real_estate
        assert "area_for_exclusive_use_pyung" in real_estate
        assert "area_for_exclusive_use_price_per_pyung" in real_estate


@pytest.mark.django_db(transaction=True)
def test_get_real_estates_on_map_view(client, get_jwt, create_real_estate, create_deal):
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
        "zoom_level": 6,
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


@pytest.mark.django_db(transaction=True)
def test_get_region_prices_on_map_view(
    client,
    get_jwt,
    create_region,
    create_region_price,
):
    """
    zool_level에 따라 시군구동읍면리 단위로 평균 매매가, 평균 평당가 등 응답
    """
    region = create_region(
        sido="서울특별시",
        sigungu="서초구",
        ubmyundong="논현동",
        dongri="논현동",
        latitude=37.5054,
        longitude=127.0216,
    )

    create_region_price(
        region_id=region.id,
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

    """TODO
      region_price 테이블 채우기
      zoom_level 변경 시 응답 asssert
    """
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
        "zoom_level": 5,
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

        assert "latitude" in region
        assert "longitude" in region


@pytest.mark.django_db(transaction=True)
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


@pytest.mark.django_db(transaction=True)
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

    data = response.json()
    real_estate = data.get("data")
    assert real_estate["id"] == real_estate1.id
    assert real_estate["name"] == real_estate1.name
    assert real_estate["build_year"] == real_estate1.build_year
    assert real_estate["regional_code"] == real_estate1.regional_code
    assert real_estate["lot_number"] == real_estate1.lot_number
    assert real_estate["road_name_address"] == real_estate1.road_name_address
    assert real_estate["real_estate_type"] == real_estate1.real_estate_type
    assert real_estate["latitude"] == real_estate1.latitude
    assert real_estate["longitude"] == real_estate1.longitude
    assert "deals" in real_estate

    deals = real_estate["deals"]
    for deal in deals:
        assert "deal_price" in deal
        assert "brokerage_type" in deal
        assert "deal_year" in deal
        assert "land_area" in deal
        assert "deal_month" in deal
        assert "deal_day" in deal
        assert "area_for_exclusive_use_pyung" in deal
        assert "area_for_exclusive_use_price_per_pyung" in deal
        assert "deal_type" in deal
