from typing import Dict

from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from modu_property.utils.loggers import logger
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from real_estate.enum.real_estate_enum import SearchLimitEnum
from real_estate.exceptions import (
    SearchAndUpdateRealEstatesException,
    NotFoundException,
)
from real_estate.schema.real_estate_view_schema import (
    get_real_estates_on_search_view_get_decorator,
)
from real_estate.serializers import GetRealEstatesOnSearchRequestSerializer
from real_estate.services.get_real_estates_on_search_service import (
    GetRealEstatesOnSearchService,
)


class GetRealEstatesOnSearchView(ListAPIView):
    serializer_class = GetRealEstatesOnSearchRequestSerializer
    pagination_class = None

    @get_real_estates_on_search_view_get_decorator
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Response:
        dto = self.get_dto(kwargs, request)
        try:
            result: Dict = GetRealEstatesOnSearchService().get_real_estates(
                dto=dto
            )
            return Response(data=result)
        except NotFoundException as e:
            logger.exception(msg="")
            return Response(status=e.status_code)
        except SearchAndUpdateRealEstatesException as e:
            logger.exception(msg="")
            return Response(status=e.status_code)

    def get_dto(self, kwargs, request):
        request_data = {
            "deal_type": kwargs["deal_type"],
            "keyword": request.query_params.get("keyword", ""),
            "real_estate_search_limit": request.query_params.get(
                "real_estate_search_limit"
            ),
        }
        serializer = self.get_serializer(
            data=request_data,
        )
        serializer.is_valid(raise_exception=True)
        dto = GetRealEstatesOnSearchDto(**serializer.validated_data)
        return dto
