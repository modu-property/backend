from django.http import JsonResponse
from django.urls import reverse
from real_estate.enum.deal_enum import DealType
from tests.conftests.real_estate_conftest import *
from tests.conftests.account_conftest import get_jwt
from django.contrib.gis.geos import Point


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
        latitude="37.5054",
        longitude="127.0216",
        point=Point(37.5054, 127.0216),
    )

    create_deal(
        real_estate_id=real_estate1.id,
        deal_price=10000,
        deal_type="DIRECT_DEAL",
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
        type=DealType.DEAL,
    )

    real_estate2 = create_real_estate(
        name="OAK 빌",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 서초구 반포동 734-32 반포엠",
        road_name_address="서울특별시 서초구 사평대로53길 30 (반포동)",
        address="서울특별시 서초구 반포동 734-32 반포엠",
        latitude="37.5056",
        longitude="127.0215",
        point=Point(37.5056, 127.0215),
    )

    create_deal(
        real_estate_id=real_estate2.id,
        deal_price=20000,
        deal_type="BROKERAGE_DEAL",
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
        type=DealType.DEAL,
    )

    real_estate3 = create_real_estate(
        name="봉은사로 빌라",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 강남구 논현동 175-19",
        road_name_address="서울특별시 강남구 봉은사로25길 34 (논현동)",
        address="서울특별시 강남구 논현동 175-19",
        latitude="37.5094",
        longitude="127.0321",
        point=Point(37.5094, 127.0321),
    )

    create_deal(
        real_estate_id=real_estate3.id,
        deal_price=30000,
        deal_type="BROKERAGE_DEAL",
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
        type=DealType.DEAL,
    )

    real_estate4 = create_real_estate(
        name="지산로얄빌라",
        build_year=1990,
        regional_code="21070",
        lot_number="부산광역시 남구 대연동 1724-1",
        road_name_address="부산광역시 남구 유엔로157번나길 48 (대연동, 지산로얄빌라)",
        address="부산광역시 남구 대연동 1724-1",
        latitude="35.133",
        longitude="129.0959",
        point=Point(35.133, 129.0959),
    )

    create_deal(
        real_estate_id=real_estate4.id,
        deal_price=30000,
        deal_type="BROKERAGE_DEAL",
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
        type=DealType.DEAL,
    )

    url = reverse("get-real-estates-on-map", kwargs={"type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "latitude": 37.5054,
        "longitude": 127.0216,
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
        assert "area_for_exclusive_use_pyung" in real_estate
        assert "area_for_exclusive_use_price_per_pyung" in real_estate


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
    url = reverse("get-real-estates-on-search", kwargs={"type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "keyword": "반포",
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
        latitude="37.5054",
        longitude="127.0216",
        point=Point(37.5054, 127.0216),
    )

    create_deal(
        real_estate_id=real_estate1.id,
        deal_price=10000,
        deal_type="DIRECT_DEAL",
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
        type=DealType.DEAL,
    )

    create_deal(
        real_estate_id=real_estate1.id,
        deal_price=20000,
        deal_type="BROKERAGE_DEAL",
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
        type=DealType.DEAL,
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
    assert real_estate["latitude"] == real_estate1.latitude
    assert real_estate["longitude"] == real_estate1.longitude
    assert "SRID=4326;POINT" in real_estate["point"]
    assert "deals" in real_estate

    deals = real_estate["deals"]
    for deal in deals:
        assert "deal_price" in deal
        assert "deal_type" in deal
        assert "deal_year" in deal
        assert "land_area" in deal
        assert "deal_month" in deal
        assert "deal_day" in deal
        assert "area_for_exclusive_use_pyung" in deal
        assert "area_for_exclusive_use_price_per_pyung" in deal
        assert "type" in deal
