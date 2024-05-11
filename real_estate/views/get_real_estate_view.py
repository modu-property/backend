from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
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
    pagination_class = None

    @get_real_estate_view_get_decorator
    def get(self, request: Request, *args, **kwargs) -> Response:
        response: Response = super().retrieve(request, *args, **kwargs)
        return response
