from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator
from real_estate.dto.real_estate_dto import GetDealPriceOfRealEstateDto
from real_estate.serializers import (
    GetRealEstateByIdSerializer,
    GetRealEstateRequestSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchTabResponseSerializer,
)
from real_estate.services.get_deal_price_of_real_estate_service import (
    GetDealPriceOfRealEstateService,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    PolymorphicProxySerializer,
)
from rest_framework.serializers import BaseSerializer
from modu_property.utils.loggers import logger


class RealEstateView(ListAPIView):
    @extend_schema(
        summary="부동산 조회",
        description="keyword로 검색하거나 latitude, longitude으로 요청",
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=False,
            ),
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="real_estate_id",
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
            OpenApiParameter(
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색어",
                required=False,
            ),
        ],
        request=GetRealEstateRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstates",
                serializers=[
                    GetRealEstatesOnSearchTabResponseSerializer,
                    GetRealEstatesOnMapResponseSerializer,
                    GetRealEstateByIdSerializer,
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
            "id": request.query_params.get("id", 0) and int(request.query_params["id"]),
            "type": kwargs["type"],
            "latitude": request.query_params.get("latitude", 0.0),
            "longitude": request.query_params.get("longitude", 0.0),
            "zoom_level": request.query_params.get("zoom_level", 0),
            "keyword": request.query_params.get("keyword", ""),
        }

        try:
            serializer = GetRealEstateRequestSerializer(data=request_data)
        except Exception as e:
            logger.error(f"RealEstateView e : {e}")
            return JsonResponse(data={}, status=400)

        is_valid = serializer.is_valid()
        if not is_valid:
            logger.error(f"serializer.errors {serializer.errors}")

        validated_data = serializer.validated_data
        dto = GetDealPriceOfRealEstateDto(**validated_data)
        result = GetDealPriceOfRealEstateService().execute(dto=dto)

        if not result:
            return JsonResponse(data={}, status=404)

        if isinstance(result, BaseSerializer):
            if result.is_valid():
                return JsonResponse(
                    data=result.validated_data,
                    status=200,
                    safe=False,
                )

        return JsonResponse(
            data=result,
            status=200,
            safe=False,
        )
