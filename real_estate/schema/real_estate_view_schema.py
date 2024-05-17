from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    PolymorphicProxySerializer,
    OpenApiExample,
)

from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.serializers import (
    GetDealsRequestSerializer,
    GetRealEstateResponseSerializer,
    GetRealEstateRequestSerializer,
    GetRealEstatesAndRegionsOnSearchResponseSerializer,
    GetRealEstatesOnMapRequestSerializer,
    GetRealEstatesOnMapResponseSerializer,
    GetRealEstatesOnSearchRequestSerializer,
    GetRegionsOnMapResponseSerializer,
    DealDictSerializer,
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
                examples=[
                    OpenApiExample(
                        name="real_estate_id",
                        description="real_estate_id",
                        value="30000",
                    ),
                ],
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
                        value=DealTypesForDBEnum.DEAL.value,
                    ),
                    OpenApiExample(
                        name="전세",
                        description="전세 타입",
                        value="JEONSE",
                    ),
                    OpenApiExample(
                        name="월세",
                        description="월세 타입",
                        value="MONTHLY_RENT",
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
                name="real_estate_search_limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="몇 개 보여줄 지 결정, regions는 3개로 고정",
                required=False,
                default=15,
                examples=[
                    OpenApiExample(
                        name="최소 limit",
                        description="최소 limit",
                        value="15",
                    ),
                    OpenApiExample(
                        name="최대 limit",
                        description="최대 limit",
                        value="50",
                    ),
                ],
            ),
        ],
        request=GetRealEstatesOnSearchRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstatesAndRegions",
                serializers=[
                    GetRealEstatesAndRegionsOnSearchResponseSerializer
                ],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
            404: OpenApiResponse(description="not found"),
        },
    )(view_function)

    return decorated_view_function


def get_real_estates_on_map_view_get_decorator(view_function):
    decorated_view_function = extend_schema(
        summary="latitude, longitude, zoom_level로 부동산 조회",
        description="latitude, longitude, zoom_level로 부동산 조회",
        parameters=[
            OpenApiParameter(
                name="deal_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal, jeonse, monthly_rent",
                required=True,
                default="deal",
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
                name="sw_lat",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 남서측 위도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="서울 남서측 위도",
                        description="남서측 위도",
                        value="37.54296876065889",
                    ),
                    OpenApiExample(
                        name="강원도 횡성군 남서측 위도",
                        description="강원도 횡성군 남서측 위도",
                        value="37.4825868",
                    ),
                ],
            ),
            OpenApiParameter(
                name="sw_lng",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 남서측 경도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="서울 남서측 경도",
                        description="남서측 경도",
                        value="126.9714256618418",
                    ),
                    OpenApiExample(
                        name="강원도 횡성군 남서측 경도",
                        description="강원도 횡성군 남서측 경도",
                        value="127.9014549",
                    ),
                ],
            ),
            OpenApiParameter(
                name="ne_lat",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 북동측 위도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="북동측 위도",
                        description="북동측 위도",
                        value="37.55780157762771",
                    ),
                    OpenApiExample(
                        name="강원도 속초 북동측 위도",
                        description="강원도 북동측 위도",
                        value="38.2622783",
                    ),
                ],
            ),
            OpenApiParameter(
                name="ne_lng",
                type=float,
                location=OpenApiParameter.QUERY,
                description="지도상의 북동측 경도",
                required=True,
                examples=[
                    OpenApiExample(
                        name="북동측 경도",
                        description="북동측 경도",
                        value="126.98407317806495",
                    ),
                    OpenApiExample(
                        name="강원도 속초 북동측 경도",
                        description=" 강원도 속초 북동측 경도",
                        value="128.5011757",
                    ),
                ],
            ),
            OpenApiParameter(
                name="zoom_level",
                type=int,
                location=OpenApiParameter.QUERY,
                description="줌 레벨",
                required=True,
                examples=[
                    OpenApiExample(
                        name="줌 레벨 5",
                        description="5 이하면 150개의 개별 부동산 정보를 응답함",
                        value="5",
                    ),
                    OpenApiExample(
                        name="줌 레벨 6",
                        description="6 이상 9이하면 20개의 지역 부동산 정보를 응답함",
                        value="6",
                    ),
                ],
            ),
        ],
        request=GetRealEstatesOnMapRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="RealEstates",
                serializers=[
                    GetRealEstatesOnMapResponseSerializer,
                    GetRegionsOnMapResponseSerializer,
                ],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
        },
    )(view_function)

    return decorated_view_function


def get_deals_view_get_decorator(view_function):
    decorated_view_function = extend_schema(
        summary="page 번호로 거래내역 조회",
        description="page 번호로 거래내역 조회",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="real_estate_id",
                required=True,
                examples=[
                    OpenApiExample(
                        name="id",
                        description="real_estate_id",
                        value="30000",
                    ),
                ],
            ),
            OpenApiParameter(
                name="deal_type",
                type=str,
                location=OpenApiParameter.PATH,
                description="deal_type",
                required=True,
                examples=[
                    OpenApiExample(
                        name="deal_type",
                        description="deal_type",
                        value=DealTypesForDBEnum.DEAL.value,
                    ),
                ],
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="조회할 페이지 번호",
                required=True,
                examples=[
                    OpenApiExample(
                        name="page",
                        description="한 페이지 당 최대 10개 거래내역 조회",
                        value="1",
                    ),
                ],
            ),
        ],
        request=GetDealsRequestSerializer,
        responses={
            200: PolymorphicProxySerializer(
                component_name="Deals",
                serializers=[DealDictSerializer],
                resource_type_field_name=None,
            ),
            400: OpenApiResponse(description="bad request"),
            404: OpenApiResponse(description="not found"),
        },
    )(view_function)

    return decorated_view_function
