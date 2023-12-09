import logging
from typing import Union
import manticoresearch

from manticoresearch.api import search_api
from manticoresearch.model.search_request import SearchRequest
from real_estate.dto.real_estate_dto import GetDealPriceOfRealEstateDto
from real_estate.models import RealEstate
from real_estate.serializers import (
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchTabResponseSerializer,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F

logger = logging.getLogger("django")


class GetDealPriceOfRealEstateService:
    def get_distance_tolerance(self, dto: GetDealPriceOfRealEstateDto):
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

    def get_real_estates_by_lat_and_long(
        self, dto: GetDealPriceOfRealEstateDto, distance_tolerance: int
    ):
        center_point = Point(
            float(dto.latitude), float(dto.longitude), srid=4326
        )  # 위경도 받아서 지도의 중심으로 잡음

        real_estates = (
            RealEstate.objects.prefetch_related("deal")
            .annotate(
                distance=Distance("point", center_point),
                area_for_exclusive_use_pyung=F("deal__area_for_exclusive_use_pyung"),
                area_for_exclusive_use_price_per_pyung=F(
                    "deal__area_for_exclusive_use_price_per_pyung"
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
        logger.debug(real_estates)

        return real_estates

    def get_real_estates_by_keyword(self, dto: GetDealPriceOfRealEstateDto):
        real_estates = RealEstate.objects.all()
        logger.debug(f"real_estate : {real_estates}")

        configuration = manticoresearch.Configuration(host="http://0.0.0.0:9308")

        api_client = manticoresearch.ApiClient(configuration)

        search_instance = search_api.SearchApi(api_client)

        search_request = SearchRequest(
            index="real_estate",
            query={"query_string": f"@* *{dto.keyword}*"},
        )

        search_response = search_instance.search(search_request)
        hits = search_response.hits
        if not hits:
            return []
        hits = hits.hits

        real_estates = []
        for hit in hits:
            hit["_source"]["id"] = int(hit["_id"])
            real_estates.append(hit["_source"])

        return real_estates

    def execute(
        self, dto: GetDealPriceOfRealEstateDto
    ) -> Union[
        list,
        GetRealEstatesOnMapResponseSerializer,
        GetRealEstatesOnSearchTabResponseSerializer,
    ]:
        # zoom_level에 맞게 반경 지정하는 메서드 만들기
        # keyword가 있으면 그 검색어에 맞는 거 추출(manticore 사용?)하고 그곳의 latitude, longitude 구해서 반경 내에 속하는 것들 추출
        # keyword 없고 latitude, longitude 있으면  반경 내에 속하는 것들 추출

        real_estates = []
        if not dto.keyword and dto.latitude and dto.longitude:
            distance_tolerance = self.get_distance_tolerance(dto=dto)
            real_estates = self.get_real_estates_by_lat_and_long(
                dto, distance_tolerance=distance_tolerance
            )
            if real_estates:
                return GetRealEstatesOnMapResponseSerializer(
                    data=list(real_estates), many=True
                )
            return []

        elif dto.keyword and not dto.latitude and not dto.longitude:
            real_estates = self.get_real_estates_by_keyword(dto=dto)
            if real_estates:
                return GetRealEstatesOnSearchTabResponseSerializer(
                    data=list(real_estates), many=True
                )
