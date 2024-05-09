from typing import Any
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView

from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import (
    GetRealEstatesOnMapDto,
)
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import RealEstateZoomLevelEnum
from real_estate.serializers import (
    GetRealEstatesOnMapRequestSerializer,
)

from real_estate.services.get_real_estates_on_map_service import (
    GetPropertiesOnMapService,
)
from real_estate.schema.real_estate_view_schema import (
    get_real_estates_on_map_view_get_decorator,
)


class GetRealEstatesOnMapView(ListAPIView):
    @get_real_estates_on_map_view_get_decorator
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
                "zoom_level", default=RealEstateZoomLevelEnum.DEFAULT.value
            ),
        }

        data: Any = validate_data(
            data=request_data,
            serializer=GetRealEstatesOnMapRequestSerializer,
        )
        if not data:
            return JsonResponse(data={}, status=400)

        dto = GetRealEstatesOnMapDto(**data)
        result: ServiceResultDto = GetPropertiesOnMapService().get_properties(
            dto=dto
        )

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )
