from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator
from property.dto.villa_dto import GetDealPriceOfVillaDto
from property.serializers import (
    GetVillaRequestSerializer,
    GetVillasOnMapResponseSerializer,
    GetVillasOnSearchTabResponseSerializer,
)
from property.services.get_deal_price_of_villa_service import GetDealPriceOfVillaService
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    PolymorphicProxySerializer,
)


class VillaView(ListAPIView):
    @extend_schema(
        summary="빌라 조회",
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
        request=GetVillaRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="Villas",
                serializers=[
                    GetVillasOnSearchTabResponseSerializer,
                    GetVillasOnMapResponseSerializer,
                ],
                resource_type_field_name=None,
                # many=True,
            ),
            400: OpenApiResponse(description="bad request"),
        },
    )
    @jwt_authenticator
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
        serializer = GetVillaRequestSerializer(data=request_data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            dto = GetDealPriceOfVillaDto(**validated_data)
            villas_response_serializer = GetDealPriceOfVillaService().execute(dto=dto)

            if not villas_response_serializer:
                return JsonResponse(data={}, status=404)

            if villas_response_serializer.is_valid():
                return JsonResponse(
                    data=villas_response_serializer.validated_data,
                    status=200,
                    safe=False,
                )
