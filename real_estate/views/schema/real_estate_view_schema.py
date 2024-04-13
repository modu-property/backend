from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    PolymorphicProxySerializer,
    OpenApiExample,
)

from real_estate.serializers import (
    GetRealEstateResponseSerializer,
    GetRealEstateRequestSerializer,
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
    GetRealEstatesOnSearchRequestSerializer,
)


def get_real_estate_view_get_decorator(view_function):
    decorated_view_function = extend_schema(
        summary="부동산 id로 단일 부동산 조회",
        description="id로 real_estate_id 입력",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="real_estate_id",
                required=True,
            )
        ],
        request=GetRealEstateRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstate",
                serializers=[
                    GetRealEstateResponseSerializer,
                ],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
            404: OpenApiResponse(description="not found"),
        },
    )(view_function)

    return decorated_view_function


def get_real_estates_on_search_view_get_decorator(view_function):
    decorated_view_function = extend_schema(
        summary="keyword로 부동산 조회",
        description="keyword로 부동산 조회",
        parameters=[
            OpenApiParameter(
                name="deal_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=True,
                examples=[
                    OpenApiExample(
                        name="매매",
                        description="매매 타입",
                        value="deal",
                    ),
                    OpenApiExample(
                        name="전세",
                        description="전세 타입",
                        value="jeonse",
                    ),
                    OpenApiExample(
                        name="월세",
                        description="월세 타입",
                        value="monthly_rent",
                    ),
                ],
            ),
            OpenApiParameter(
                name="keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색어",
                required=True,
                examples=[
                    OpenApiExample(
                        name="강남",
                        description="강남",
                        value="강남",
                    ),
                    OpenApiExample(
                        name="하안미리",
                        description="하안미리",
                        value="하안미리",
                    ),
                    OpenApiExample(
                        name="부산",
                        description="부산",
                        value="부산",
                    ),
                ],
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="몇 개 보여줄 지 결정, regions는 3개로 고정",
                required=False,
                default=10,
                examples=[
                    OpenApiExample(
                        name="최소 limit",
                        description="최소 limit",
                        value="10",
                    ),
                    OpenApiExample(
                        name="최대 limit",
                        description="최대 limit",
                        value="30",
                    ),
                ],
            ),
        ],
        request=GetRealEstatesOnSearchRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstatesAndRegions",
                serializers=[GetRealEstatesAndRegionsOnSearchResponseSerializer],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
            404: OpenApiResponse(description="not found"),
        },
    )(view_function)

    return decorated_view_function
