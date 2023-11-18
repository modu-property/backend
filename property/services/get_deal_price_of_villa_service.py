import logging
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
        self.logger = logging.getLogger("django")

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
        self.logger.debug("get_villas_by_lat_and_long!")
        center_point = Point(
            float(dto.latitude), float(dto.longitude), srid=4326
        )  # 위경도 받아서 지도의 중심으로 잡음

        self.logger.debug("get all villa")
        villas = Villa.objects.all()
        self.logger.debug(f"villa : {villas}")

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
        self.logger.debug(villas)

        return villas

    def get_villas_by_keyword(self, dto: GetDealPriceOfVillaDto):
        configuration = manticoresearch.Configuration(host="http://0.0.0.0:9308")

        api_client = manticoresearch.ApiClient(configuration)

        # with manticoresearch.ApiClient(configuration) as api_client:
        search_instance = search_api.SearchApi(api_client)

        search_request = SearchRequest(
            index="villa",
            query={"query_string": f"@* *{dto.keyword}*"},
        )

        search_response = search_instance.search(search_request)
        hits = search_response.hits
        if not hits:
            return []
        hits = hits.hits

        villas = []
        for hit in hits:
            hit["_source"]["id"] = int(hit["_id"])
            villas.append(hit["_source"])

        return villas

    def execute(
        self, dto: GetDealPriceOfVillaDto
    ) -> Union[
        list, GetVillasOnMapResponseSerializer, GetVillasOnSearchTabResponseSerializer
    ]:
        # zoom_level에 맞게 반경 지정하는 메서드 만들기
        # keyword가 있으면 그 검색어에 맞는 거 추출(manticore 사용?)하고 그곳의 latitude, longitude 구해서 반경 내에 속하는 것들 추출
        # keyword 없고 latitude, longitude 있으면  반경 내에 속하는 것들 추출

        villas = []
        if not dto.keyword and dto.latitude and dto.longitude:
            distance_tolerance = self.get_distance_tolerance(dto=dto)
            villas = self.get_villas_by_lat_and_long(
                dto, distance_tolerance=distance_tolerance
            )
            if villas:
                return GetVillasOnMapResponseSerializer(data=list(villas), many=True)
            return []

        elif dto.keyword and not dto.latitude and not dto.longitude:
            villas = self.get_villas_by_keyword(dto=dto)
            if villas:
                return GetVillasOnSearchTabResponseSerializer(
                    data=list(villas), many=True
                )
