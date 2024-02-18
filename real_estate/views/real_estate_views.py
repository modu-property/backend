from typing import Any
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import (
    GetRealEstateDto,
    GetRealEstatesOnMapDto,
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstateRequestSerializer,
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
    GetRealEstatesOnMapRequestSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchRequestSerializer,
)
from real_estate.services.get_deal_price_of_real_estate_service import (
    GetRealEstatesOnMapService,
    GetRealEstateService,
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


class GetRealEstateView(APIView):
    @extend_schema(
        summary="부동산 id로 단일 부동산, 거래내역 조회",
        description="id로 real_estate_id 입력",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="real_estate_id",
                required=True,
            )
        ],
        request=GetRealEstateRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstate",
                serializers=[
                    GetRealEstateResponseSerializer,
                ],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
            404: OpenApiResponse(description="not found"),
        },
    )
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
        result: ServiceResultDto = GetRealEstateService().execute(dto=dto)

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )


class GetRealEstatesOnSearchView(ListAPIView):
    @extend_schema(
        summary="keyword로 부동산 조회",
        description="keyword로 부동산 조회",
        parameters=[
            OpenApiParameter(
                name="deal_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=True,
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
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색어",
                required=True,
                examples=[
                    OpenApiExample(
                        name="강남",
                        description="강남",
                        value="강남",
                    ),
                    OpenApiExample(
                        name="하안미리",
                        description="하안미리",
                        value="하안미리",
                    ),
                    OpenApiExample(
                        name="부산",
                        description="부산",
                        value="부산",
                    ),
                ],
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="몇 개 보여줄 지 결정, regions는 3개로 고정",
                required=False,
                default=10,
                examples=[
                    OpenApiExample(
                        name="최소 limit",
                        description="최소 limit",
                        value="10",
                    ),
                    OpenApiExample(
                        name="최대 limit",
                        description="최대 limit",
                        value="30",
                    ),
                ],
            ),
        ],
        request=GetRealEstatesOnSearchRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstatesAndRegions",
                serializers=[GetRealEstatesAndRegionsOnSearchResponseSerializer],
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
        result: ServiceResultDto = GetRealEstatesOnSearchService().execute(dto=dto)

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
                name="latitude",
                type=float,
                location=OpenApiParameter.QUERY,
                description="중심 위도",
                required=False,
                examples=[
                    OpenApiExample(
                        name="위도",
                        description="서울 위도",
                        value="37.566826004661",
                    ),
                ],
            ),
            OpenApiParameter(
                name="longitude",
                type=float,
                location=OpenApiParameter.QUERY,
                description="중심 경도",
                required=False,
                examples=[
                    OpenApiExample(
                        name="경도",
                        description="경도",
                        value="126.978652258309",
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
                        name="남서측 위도",
                        description="남서측 위도",
                        value="37.54296876065889",
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
                        name="남서측 경도",
                        description="남서측 경도",
                        value="126.9714256618418",
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
                        name="줌 레벨 6",
                        description="6",
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
            "latitude": request.query_params.get("latitude", default=37.566826004661),
            "longitude": request.query_params.get(
                "longitude", default=126.978652258309
            ),
            "sw_lat": request.query_params.get("sw_lat"),
            "sw_lng": request.query_params.get("sw_lng"),
            "ne_lat": request.query_params.get("ne_lat"),
            "ne_lng": request.query_params.get("ne_lng"),
            "zoom_level": request.query_params.get("zoom_level", default=6),
        }

        data: Any = validate_data(
            data=request_data,
            serializer=GetRealEstatesOnMapRequestSerializer,
        )
        if not data:
            return JsonResponse(data={}, status=400)

        dto = GetRealEstatesOnMapDto(**data)
        result: ServiceResultDto = GetRealEstatesOnMapService().execute(dto=dto)

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )
