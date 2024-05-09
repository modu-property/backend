from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.schema.real_estate_view_schema import (
    get_real_estates_on_search_view_get_decorator,
)
from real_estate.serializers import GetRealEstatesOnSearchRequestSerializer
from real_estate.services.get_real_estates_on_search_service import (
    GetRealEstatesOnSearchService,
)


class GetRealEstatesOnSearchView(ListAPIView):

    serializer_class = GetRealEstatesOnSearchRequestSerializer

    @get_real_estates_on_search_view_get_decorator
    # @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Response:
        request_data = {
            "deal_type": str(kwargs["deal_type"]).upper(),
            "keyword": request.query_params.get("keyword", ""),
            "limit": request.query_params.get("limit", 10),
        }
        serializer = self.get_serializer(
            data=request_data,
        )
        serializer.is_valid(raise_exception=True)

        dto = GetRealEstatesOnSearchDto(**serializer.validated_data)
        result: ServiceResultDto = (
            GetRealEstatesOnSearchService().get_real_estates(dto=dto)
        )

        return Response(
            data=result.data,
            status=result.status_code,
        )
