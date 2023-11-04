"""
클라이언트로부터 검색어 받기
검색어에 해당하는 위경도 구하기
위경도 반경 몇미터에 있는 빌라들 구해서 응답하기

"""
from typing import Union
import manticoresearch

from manticoresearch.api import search_api
from manticoresearch.model.search_request import SearchRequest
from property.dto.villa_dto import GetDealPriceOfVillaDto
from property.models import Villa
from property.serializers import (
    GetVillasOnMapResponseSerializer,
    GetVillasOnSearchTabResponseSerializer,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F


class GetDealPriceOfVillaService:
    def __init__(self) -> None:
        pass

    def get_distance_tolerance(self, dto: GetDealPriceOfVillaDto):
        # TODO level은 임시로 정함, 바꿔야함
        zoom_levels = {
            1: 1000 * 1000,
            2: 1000 * 500,
            3: 1000 * 250,
            4: 1000 * 100,
            5: 1000 * 50,
            6: 1000 * 25,
            7: 1000 * 10,
            8: 1000 * 5,
            9: 1000 * 2,
            10: 1000 * 1,
        }
        return zoom_levels[dto.zoom_level]

    def get_villas_by_lat_and_long(
        self, dto: GetDealPriceOfVillaDto, distance_tolerance: int
    ):
        center_point = Point(
            float(dto.latitude), float(dto.longitude), srid=4326
        )  # 위경도 받아서 지도의 중심으로 잡음

        villas = (
            Villa.objects.prefetch_related("villa_deal")
            .annotate(
                distance=Distance("point", center_point),
                area_for_exclusive_use_pyung=F(
                    "villa_deal__area_for_exclusive_use_pyung"
                ),
                area_for_exclusive_use_price_per_pyung=F(
                    "villa_deal__area_for_exclusive_use_price_per_pyung"
                ),
            )
            .filter(distance__lte=distance_tolerance)
            .values(
                "id",
                "latitude",
                "longitude",
                "area_for_exclusive_use_pyung",
                "area_for_exclusive_use_price_per_pyung",
            )
        )

        return villas

    def get_villas_by_keyword(self):
        pass

    def execute(
        self, dto: GetDealPriceOfVillaDto
    ) -> Union[
        list, GetVillasOnMapResponseSerializer, GetVillasOnSearchTabResponseSerializer
    ]:
        # zoom_level에 맞게 반경 지정하는 메서드 만들기
        # keyword가 있으면 그 검색어에 맞는 거 추출(manticore 사용?)하고 그곳의 latitude, longitude 구해서 반경 내에 속하는 것들 추출
        # keyword 없고 latitude, longitude 있으면  반경 내에 속하는 것들 추출

        villas = []
        # ST_Distance
        if not dto.keyword and dto.latitude and dto.longitude:
            distance_tolerance = self.get_distance_tolerance(dto)
            villas = self.get_villas_by_lat_and_long(
                dto, distance_tolerance=distance_tolerance
            )
            if villas:
                return GetVillasOnMapResponseSerializer(data=list(villas), many=True)
            return []

        elif dto.keyword and not dto.latitude and not dto.longitude:
            self.get_villas_by_keyword()

        configuration = manticoresearch.Configuration(host="http://0.0.0.0:9308")

        with manticoresearch.ApiClient(configuration) as api_client:
            search_instance = search_api.SearchApi(api_client)

            search_request = SearchRequest(
                index="property_villa",
                query={"query_string": "@dong 반포*"},
            )

            api_response1 = search_instance.search(search_request)
            print(f"hits 1 {api_response1.hits}")

            search_request = SearchRequest(
                index="property_villa",
                query={"query_string": "@dong *포동"},
            )

            api_response2 = search_instance.search(search_request)
            print(f"hits 2 {api_response2.hits}")

            return
            # from manticoresearch.model.query_filter import QueryFilter

            # search_request.fulltext_filter = QueryFilter("연수동")
            # api_response = search_instance.search(search_request)
            # print(api_response.hits)

            # search_request.fulltext_filter = QueryFilter("연")
            # api_response = search_instance.search(search_request)
            # print(api_response.hits)

            # from manticoresearch.model.match_filter import MatchFilter

            # search_request.fulltext_filter = MatchFilter("@dong 연수*")
            # api_response = search_instance.search(search_request)
            # print(api_response.hits)

            # search_request.fulltext_filter = MatchFilter("@dong 연*")
            # api_response = search_instance.search(search_request)
            # print(f"api_response.hits {api_response}")

            # from manticoresearch.model.fulltext_filter import FulltextFilter

            # search_request.fulltext_filter = FulltextFilter("연수동")
            # api_response = search_instance.search(search_request)
            # print(api_response.hits)

            # search_request.fulltext_filter = FulltextFilter("연")
            # api_response = search_instance.search(search_request)
            # print(api_response.hits)

            try:
                api_response = search_instance.search(search_request)
                hits = api_response.hits
                if not hits:
                    return {}, "검색 결과 없음"
                _hits = hits.hits
                villas = []
                for hit in _hits:
                    source = hit["_source"]
                    source["id"] = int(hit["_id"])
                    serializer = GetVillasOnSearchTabResponseSerializer(data=source)
                    if serializer.is_valid():
                        validated_data = serializer.validated_data

                        villas.append(dict(validated_data))
                    else:
                        print(f"VillaView get invalid source : {source}")
                return villas, "빌라 찾음"
            except manticoresearch.ApiException as e:
                message = f"Exception when calling SearchApi->search e: {e}"
                return {}, message
            except Exception as e:
                message = f"VillaView get e: {e}"
                return {}, message
