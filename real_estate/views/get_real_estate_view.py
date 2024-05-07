from typing import Any

from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView
from modu_property.utils.loggers import logger
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetRealEstateDto
from real_estate.dto.service_result_dto import ServiceResultDto

from real_estate.schema.real_estate_view_schema import (
    get_real_estate_view_get_decorator,
)
from real_estate.serializers import GetRealEstateRequestSerializer
from real_estate.services.get_real_estate_service import GetRealEstateService


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
        result: ServiceResultDto = GetRealEstateService().get_real_estate(
            dto=dto
        )

        return JsonResponse(
            data=result.data,
            status=result.status_code,
            safe=False,
        )
