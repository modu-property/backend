import os
from django.urls import reverse

from tests.fixtures import *

# TODO
"""
***** 먼저, 매매 정보를 DB에 넣고 indexer 실행해서 manticore가 검색할 데이터를 만들어야 함

parametrize 써서 연*, 연수*, *수* 등등 체크하기
검색 keyword에 동, 도로명주소, 지번, 이름

"""


@pytest.mark.django_db(transaction=True)
def test_get_villas_with_latitude_longitude_zoom_level_view(
    client, get_jwt, create_villa, create_villa_deal
):
    villa1 = create_villa(
        name="테스트빌라 1",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 서초구 사평대로53길 22 (반포동)",
        road_name_address="서울특별시 서초구 반포동 739",
        latitude="37.5054",
        longitude="127.0216",
        point=Point(37.5054, 127.0216),
    )

    create_villa_deal(
        villa_id=villa1.id,
        deal_price=10000,
        deal_type="BROKERAGE_DEAL",
        deal_year=2023,
        land_area=100,
        deal_month=3,
        deal_day=21,
        area_for_exclusive_use=80,
        floor=3,
        is_deal_canceled=False,
        deal_canceld_date=None,
        area_for_exclusive_use_pyung="30.30",
        area_for_exclusive_use_price_per_pyung="330",
    )

    villa2 = create_villa(
        name="OAK 빌",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 서초구 사평대로53길 30 (반포동)",
        road_name_address="서울특별시 서초구 반포동 734-32 반포엠",
        latitude="37.5056",
        longitude="127.0215",
        point=Point(37.5056, 127.0215),
    )

    create_villa_deal(
        villa_id=villa2.id,
        deal_price=20000,
        deal_type="BROKERAGE_DEAL",
        deal_year=2023,
        land_area=200,
        deal_month=12,
        deal_day=30,
        area_for_exclusive_use=150,
        floor=5,
        is_deal_canceled=False,
        deal_canceld_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
    )

    villa3 = create_villa(
        name="봉은사로 빌라",
        build_year=1990,
        regional_code="11650",
        lot_number="서울특별시 강남구 논현동 175-19",
        road_name_address="서울특별시 강남구 봉은사로25길 34 (논현동)",
        latitude="37.5094",
        longitude="127.0321",
        point=Point(37.5094, 127.0321),
    )

    create_villa_deal(
        villa_id=villa3.id,
        deal_price=30000,
        deal_type="BROKERAGE_DEAL",
        deal_year=2022,
        land_area=150,
        deal_month=1,
        deal_day=1,
        area_for_exclusive_use=130,
        floor=2,
        is_deal_canceled=False,
        deal_canceld_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
    )

    villa4 = create_villa(
        name="지산로얄빌라",
        build_year=1990,
        regional_code="21070",
        lot_number="부산광역시 남구 대연동 1724-1",
        road_name_address="부산광역시 남구 유엔로157번나길 48 (대연동, 지산로얄빌라)",
        latitude="35.133",
        longitude="129.0959",
        point=Point(35.133, 129.0959),
    )

    create_villa_deal(
        villa_id=villa4.id,
        deal_price=30000,
        deal_type="BROKERAGE_DEAL",
        deal_year=2022,
        land_area=150,
        deal_month=1,
        deal_day=1,
        area_for_exclusive_use=130,
        floor=2,
        is_deal_canceled=False,
        deal_canceld_date=None,
        area_for_exclusive_use_pyung="60.60",
        area_for_exclusive_use_price_per_pyung="329.99",
    )

    url = reverse("villa", kwargs={"type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "latitude": 37.5054,
        "longitude": 127.0216,
        "zoom_level": 9,
        "keyword": "",
    }

    response = client.get(url, data=query_params, **headers)
    assert response.status_code == 200
    villas = response.json()
    for villa in villas:
        assert "latitude" in villa
        assert "longitude" in villa
        assert "area_for_exclusive_use_pyung" in villa
        assert "area_for_exclusive_use_price_per_pyung" in villa


# @pytest.mark.django_db
# def test_create_post_view_when_invalid_request_then_400(client, get_jwt):
#     url = reverse("create_post")

#     _jwt = get_jwt

#     headers = {"HTTP_Authorization": _jwt}
#     data = {"title": "test_title", "content": ""}

#     response = client.post(path=url, **headers, data=data)
#     assert response.status_code == 400


# @pytest.mark.django_db
# def test_get_post_view(client, create_post):
#     url = reverse("get_post", kwargs={"id": 1})
#     response = client.get(url)
#     assert response.status_code == 200
#     assert response.data["title"] == "test_title"


# @pytest.mark.django_db
# def test_get_post_view_when_no_post_then_404(client):
#     url = reverse("get_post", kwargs={"id": 1})
#     response = client.get(url)
#     assert response.status_code == 404


# @pytest.mark.django_db
# def test_get_post_list(client, create_post):
#     url = reverse("get_post_list")
#     response = client.get(url)
#     assert response.status_code == 200


# @pytest.mark.django_db
# def test_get_post_list_when_no_post_then_404(client):
#     url = reverse("get_post_list")
#     response = client.get(url)
#     assert response.status_code == 404
