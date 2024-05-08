from typing import Any

from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.request import Request

from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetDealsDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.schema.real_estate_view_schema import (
    get_deals_view_get_decorator,
)
from real_estate.serializers import GetDealsRequestSerializer
from real_estate.services.get_deals_service import GetDealsService


class GetDealsView(ListAPIView):
    @get_deals_view_get_decorator
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
