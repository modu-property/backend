from django.db.models import QuerySet
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
)
from real_estate.services.get_deals_service import GetDealsService
from real_estate.utils.paginator_util import CustomPagination


class GetDealsView(ListAPIView):
    serializer_class = DealDictSerializer
    pagination_class = CustomPagination

    def __init__(self):
        super().__init__()
        self.dto = None

    @get_deals_view_get_decorator
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Response:
        dto: GetDealsDto = GetDealsDto(
            real_estate_id=int(kwargs.get("id", 0)),
            deal_type=str(
                kwargs.get("deal_type", DealTypesForDBEnum.DEAL.value),
            ).upper(),
        )
        self.dto = dto

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self) -> QuerySet[Deal]:
        return GetDealsService().get_deals(dto=self.dto)
