from typing import Any
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator

from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import (
    GetDealsDto,
    GetRealEstateDto,
    GetRealEstatesOnMapDto,
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import RealEstateZoomLevel
from real_estate.serializers import (
    GetDealsRequestSerializer,
    GetDealsResponseSerializer,
    GetRealEstateRequestSerializer,
    GetRealEstatesOnMapRequestSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchRequestSerializer,
    GetRegionsOnMapResponseSerializer,
)
from real_estate.services.get_real_estates_on_search_service import (
    GetRealEstatesOnSearchService,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    PolymorphicProxySerializer,
    OpenApiExample,
)
from modu_property.utils.loggers import logger
from rest_framework.views import APIView
from real_estate.services.get_deals_service import GetDealsService
from manticore.manticore_client import ManticoreClient
from real_estate.services.get_real_estate_service import GetRealEstateService
from real_estate.services.get_real_estates_on_map_service import (
    GetPropertiesOnMapService,
)
from real_estate.views.schema.real_estate_view_schema import (
    get_real_estate_view_get_decorator,
    get_real_estates_on_search_view_get_decorator,
)


class GetRealEstateView(APIView):
    @get_real_estate_view_get_decorator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        logger.info(request)
        id = int(kwargs["id"]) if kwargs.get("id") else 0

        request_data: dict = {"id": id}

        data: Any = validate_data(
            data=request_data,
            serializer=GetRealEstateRequestSerializer,
        )
        if not data:
            return JsonResponse(data={}, status=400)

        dto = GetRealEstateDto(**data)
        result: ServiceResultDto = GetRealEstateService().get_real_estate(dto=dto)

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )


class GetRealEstatesOnSearchView(ListAPIView):
    @get_real_estates_on_search_view_get_decorator
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        request_data = {
            "deal_type": str(kwargs["deal_type"]).upper(),
            "keyword": request.query_params.get("keyword", ""),
            "limit": request.query_params.get("limit", 10),
        }

        data: Any = validate_data(
            data=request_data,
            serializer=GetRealEstatesOnSearchRequestSerializer,
        )
        if not data:
            return JsonResponse(data={}, status=400)

        dto = GetRealEstatesOnSearchDto(**data)
        result: ServiceResultDto = GetRealEstatesOnSearchService().get_real_estates(
            dto=dto
        )

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )


class GetRealEstatesOnMapView(ListAPIView):
    @extend_schema(
        summary="latitude, longitude, zoom_level로 부동산 조회",
        description="latitude, longitude, zoom_level로 부동산 조회",
        parameters=[
            OpenApiParameter(
                name="deal_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=True,
                default="deal",
                examples=[
                    OpenApiExample(
                        name="매매",
                        description="매매 타입",
                        value="deal",
                    ),
                    OpenApiExample(
                        name="전세",
                        description="전세 타입",
                        value="jeonse",
                    ),
                    OpenApiExample(
                        name="월세",
                        description="월세 타입",
                        value="monthly_rent",
                    ),
                ],
            ),
            OpenApiParameter(
                name="sw_lat",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 남서측 위도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="서울 남서측 위도",
                        description="남서측 위도",
                        value="37.54296876065889",
                    ),
                    OpenApiExample(
                        name="강원도 횡성군 남서측 위도",
                        description="강원도 횡성군 남서측 위도",
                        value="37.4825868",
                    ),
                ],
            ),
            OpenApiParameter(
                name="sw_lng",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 남서측 경도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="서울 남서측 경도",
                        description="남서측 경도",
                        value="126.9714256618418",
                    ),
                    OpenApiExample(
                        name="강원도 횡성군 남서측 경도",
                        description="강원도 횡성군 남서측 경도",
                        value="127.9014549",
                    ),
                ],
            ),
            OpenApiParameter(
                name="ne_lat",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 북동측 위도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="북동측 위도",
                        description="북동측 위도",
                        value="37.55780157762771",
                    ),
                    OpenApiExample(
                        name="강원도 속초 북동측 위도",
                        description="강원도 북동측 위도",
                        value="38.2622783",
                    ),
                ],
            ),
            OpenApiParameter(
                name="ne_lng",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 북동측 경도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="북동측 경도",
                        description="북동측 경도",
                        value="126.98407317806495",
                    ),
                    OpenApiExample(
                        name="강원도 속초 북동측 경도",
                        description=" 강원도 속초 북동측 경도",
                        value="128.5011757",
                    ),
                ],
            ),
            OpenApiParameter(
                name="zoom_level",
                type=int,
                location=OpenApiParameter.QUERY,
                description="줌 레벨",
                required=True,
                examples=[
                    OpenApiExample(
                        name="줌 레벨 5",
                        description="5 이하면 150개의 개별 부동산 정보를 응답함",
                        value="5",
                    ),
                    OpenApiExample(
                        name="줌 레벨 6",
                        description="6 이상 9이하면 20개의 지역 부동산 정보를 응답함",
                        value="6",
                    ),
                ],
            ),
        ],
        request=GetRealEstatesOnMapRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstates",
                serializers=[
                    GetRealEstatesOnMapResponseSerializer,
                    GetRegionsOnMapResponseSerializer,
                ],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
        },
    )
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        request_data: dict = {
            "deal_type": str(kwargs["deal_type"]).upper(),
            "sw_lat": request.query_params.get("sw_lat"),
            "sw_lng": request.query_params.get("sw_lng"),
            "ne_lat": request.query_params.get("ne_lat"),
            "ne_lng": request.query_params.get("ne_lng"),
            "zoom_level": request.query_params.get(
                "zoom_level", default=RealEstateZoomLevel.DEFAULT.value
            ),
        }

        data: Any = validate_data(
            data=request_data,
            serializer=GetRealEstatesOnMapRequestSerializer,
        )
        if not data:
            return JsonResponse(data={}, status=400)

        dto = GetRealEstatesOnMapDto(**data)
        result: ServiceResultDto = GetPropertiesOnMapService().get_properties(dto=dto)

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )


class GetDealsView(ListAPIView):
    @extend_schema(
        summary="page 번호로 거래내역 조회",
        description="page 번호로 거래내역 조회",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="real_estate_id",
                required=True,
                examples=[
                    OpenApiExample(
                        name="id",
                        description="real_estate_id",
                        value="30000",
                    ),
                ],
            ),
            OpenApiParameter(
                name="deal_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal_type",
                required=True,
                examples=[
                    OpenApiExample(
                        name="deal_type",
                        description="deal_type",
                        value="deal",
                    ),
                ],
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="조회할 페이지 번호",
                required=True,
                examples=[
                    OpenApiExample(
                        name="page",
                        description="한 페이지 당 최대 10개 거래내역 조회",
                        value="1",
                    ),
                ],
            ),
        ],
        request=GetDealsRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="Deals",
                serializers=[GetDealsResponseSerializer],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
            404: OpenApiResponse(description="not found"),
        },
    )
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        request_data: dict = {
            "real_estate_id": int(kwargs.get("id", 0)),
            "page": int(request.query_params.get("page", 1)),
            "deal_type": str(kwargs["deal_type"]).upper(),
        }

        data: Any = validate_data(
            data=request_data,
            serializer=GetDealsRequestSerializer,
        )
        if not data:
            return JsonResponse(data={}, status=400)

        dto = GetDealsDto(**data)
        result: ServiceResultDto = GetDealsService().get_deals(dto=dto)

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )


class ManticoreView(APIView):
    @extend_schema(
        summary="manticoresearch indexer 실행",
        description="manticoresearch indexer를 API 호출해서 수동 실행",
        responses={
            200: OpenApiResponse(description="ok"),
            400: OpenApiResponse(description="bad request"),
        },
    )
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        logger.info("ManticoreView")

        try:
            manticore = ManticoreClient()
            manticore.run_indexer()
            return JsonResponse(
                data={},
                status=200,
                safe=False,
            )
        except Exception as e:
            logger.error(f"celery -> django -> manticore e : {e}")
            return JsonResponse(
                data={},
                status=400,
                safe=False,
            )
