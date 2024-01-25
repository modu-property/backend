from typing import Any, OrderedDict, Union
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator
from modu_property.utils.validator import validate_model
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

        request_data = {"id": id}

        try:
            serializer = GetRealEstateRequestSerializer(data=request_data)
        except Exception as e:
            logger.error(f"RealEstateView e : {e}")
            return JsonResponse(data={}, status=400)

        is_valid = serializer.is_valid()
        if not is_valid:
            logger.error(f"serializer.errors {serializer.errors}")

        validated_data = serializer.validated_data
        dto = GetRealEstateDto(**validated_data)
        real_estate = GetRealEstateService().execute(dto=dto)

        if not real_estate:
            return JsonResponse(data={}, status=404)

        return JsonResponse(
            data=real_estate,
            status=200,
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

        try:
            serializer = GetRealEstatesOnSearchRequestSerializer(data=request_data)
        except Exception as e:
            logger.error(f"GetRealEstatesOnSearchRequestSerializer e : {e} ")
            return JsonResponse(data={}, status=400)

        is_valid = serializer.is_valid()
        if not is_valid:
            logger.error(
                f"GetRealEstatesOnSearchRequestSerializer invalid : {serializer.errors}"
            )

        validated_data = serializer.validated_data
        dto = GetRealEstatesOnSearchDto(**validated_data)
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
        request_data = {
            "type": kwargs["type"],
            "latitude": request.query_params.get("latitude", 0.0),
            "longitude": request.query_params.get("longitude", 0.0),
            "zoom_level": request.query_params.get("zoom_level", 0),
        }

        try:
            serializer = GetRealEstatesOnMapRequestSerializer(data=request_data)
        except Exception as e:
            logger.error(f"RealEGetRealEstatesOnMapRequestSerializerstateView e : {e}")
            return JsonResponse(data={}, status=400)

        is_valid = serializer.is_valid()
        if not is_valid:
            logger.error(
                f"GetRealEstatesOnMapRequestSerializer invalid : {serializer.errors}"
            )

        validated_data: Union[dict, Any] = serializer.validated_data
        dto = GetRealEstatesOnMapDto(**validated_data)
        result: ServiceResultDto = GetRealEstatesOnMapService().execute(dto=dto)

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )
