from rest_framework.generics import RetrieveAPIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.schema.real_estate_view_schema import (
    get_real_estate_view_get_decorator,
)
from real_estate.serializers import (
    GetRealEstateResponseSerializer,
)


class GetRealEstateView(RetrieveAPIView):
    queryset = RealEstateRepository.get_real_estate_all()
    serializer_class = GetRealEstateResponseSerializer
    lookup_field = "id"

    @get_real_estate_view_get_decorator
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        response: Response = super().retrieve(request, *args, **kwargs)

        if isinstance(
            request.accepted_renderer, (JSONRenderer, BrowsableAPIRenderer)
        ):
            response.data = ReturnDict(
                response.data,
                serializer=response.data.serializer,
            )
        return response
