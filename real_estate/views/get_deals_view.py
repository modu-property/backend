from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from real_estate.dto.get_real_estate_dto import GetDealsDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.models import Deal
from real_estate.schema.real_estate_view_schema import (
    get_deals_view_get_decorator,
)
from real_estate.serializers import (
    DealDictSerializer,
    GetDealsRequestSerializer,
)
from real_estate.services.get_deals_service import GetDealsService
from real_estate.utils.paginator_util import CustomPagination


class GetDealsView(ListAPIView):
    serializer_class = DealDictSerializer
    pagination_class = CustomPagination

    @get_deals_view_get_decorator
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Response:
        dto = self.get_dto(kwargs, request)

        queryset = self.get_queryset(dto)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def get_dto(kwargs, request):
        request_data = {
            "real_estate_id": kwargs.get("id"),
            "deal_type": kwargs.get("deal_type", DealTypesForDBEnum.DEAL.value),
            "page": request.query_params.get("page", 1),
        }
        request_serializer = GetDealsRequestSerializer(data=request_data)
        request_serializer.is_valid(raise_exception=True)
        return GetDealsDto(**request_serializer.validated_data)

    def get_queryset(self, dto) -> QuerySet[Deal]:
        return GetDealsService().get_deals(dto=dto)
