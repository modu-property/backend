from typing import Any
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator
from modu_property.utils.validator import validate_data
from real_estate.dto.real_estate_dto import (
    GetRealEstateDto,
    GetRealEstatesOnMapDto,
    GetRealEstatesOnSearchDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstateRequestSerializer,
    GetRealEstatesOnMapRequestSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchRequestSerializer,
    GetRealEstatesOnSearchResponseSerializer,
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
                name="type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=False,
            ),
            OpenApiParameter(
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색어",
                required=False,
            ),
        ],
        request=GetRealEstatesOnSearchRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstates",
                serializers=[
                    GetRealEstatesOnSearchResponseSerializer,
                ],
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
            "type": kwargs["type"],
            "keyword": request.query_params.get("keyword", ""),
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
                name="type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=False,
            ),
            OpenApiParameter(
                name="latitude",
                type=float,
                location=OpenApiParameter.QUERY,
                description="위도",
                required=False,
            ),
            OpenApiParameter(
                name="longitude",
                type=float,
                location=OpenApiParameter.QUERY,
                description="경도",
                required=False,
            ),
            OpenApiParameter(
                name="zoom_level",
                type=int,
                location=OpenApiParameter.QUERY,
                description="줌 레벨",
                required=False,
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
            "type": kwargs["type"],
            "latitude": request.query_params.get("latitude", 0.0),
            "longitude": request.query_params.get("longitude", 0.0),
            "zoom_level": request.query_params.get("zoom_level", 0),
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
