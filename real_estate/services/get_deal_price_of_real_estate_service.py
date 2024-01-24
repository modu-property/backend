from typing import Union
from django.forms import model_to_dict
import manticoresearch

from manticoresearch.api import search_api
from manticoresearch.model.search_request import SearchRequest
from modu_property.utils.loggers import logger
from modu_property.utils.validator import validate_model
from real_estate.dto.real_estate_dto import (
    GetDealPriceOfRealEstateDto,
    GetRealEstateDto,
)
from real_estate.models import RealEstate
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchTabResponseSerializer,
    RealEstateSerializer,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F


class GetRealEstateService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def execute(self, dto: GetRealEstateDto):
        real_estate = self.repository.get_real_estate(id=dto.id)

        try:
            serializer = GetRealEstateResponseSerializer(real_estate)
            return serializer.data
        except Exception as e:
            logger.error(f"GetRealEstateService e : {e}")
            return {}


class GetDealPriceOfRealEstateService:
    def get_distance_tolerance(self, dto: GetDealPriceOfRealEstateDto):
        # TODO level은 임시로 정함, 바꿔야함, 1,2 정도의 레벨은 하나하나 보여주지 말고 뭉쳐서 개수만 표현해야할듯..
        zoom_levels = {
            1: 10 * 10,
            2: 8 * 8,
            3: 6 * 6,
            4: 4 * 4,
            5: 2 * 2,
            6: 1 * 1,
        }
        return zoom_levels[dto.zoom_level]

    def get_real_estates_by_lat_and_long(
        self, dto: GetDealPriceOfRealEstateDto, distance_tolerance: int
    ):
        center_point = Point(
            float(dto.latitude), float(dto.longitude), srid=4326
        )  # 위경도 받아서 지도의 중심으로 잡음

        real_estates = (
            RealEstate.objects.prefetch_related("deals")
            .annotate(
                distance=Distance("point", center_point),
                area_for_exclusive_use_pyung=F("deals__area_for_exclusive_use_pyung"),
                area_for_exclusive_use_price_per_pyung=F(
                    "deals__area_for_exclusive_use_price_per_pyung"
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

    def get_real_estate_deals(self, id: int):
        try:
            real_estate_deal = (
                RealEstate.objects.filter(id=id).all().prefetch_related("deals").get()
            )
            serializer = GetRealEstateByIdSerializer(real_estate_deal)
            return serializer.data
        except Exception as e:
            logger.error(f"get_real_estate_deals e : {e}")
            return False

    def execute(
        self, dto: GetDealPriceOfRealEstateDto
    ) -> Union[
        list,
        GetRealEstatesOnMapResponseSerializer,
        GetRealEstatesOnSearchTabResponseSerializer,
        dict,
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
        elif dto.id:
            real_estate = self.get_real_estate_deals(id=dto.id)
            return real_estate

        return False
