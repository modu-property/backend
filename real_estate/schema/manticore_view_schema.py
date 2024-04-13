from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)


def get_manticore_view_get_decorator(view_function):
    decorated_view_function = extend_schema(
        summary="manticoresearch indexer 실행",
        description="manticoresearch indexer를 API 호출해서 수동 실행",
        responses={
            200: OpenApiResponse(description="ok"),
            400: OpenApiResponse(description="bad request"),
        },
    )(view_function)

    return decorated_view_function
