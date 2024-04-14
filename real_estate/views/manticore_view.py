from typing import Any
from manticore.manticore_client import SearchClientInterface

from rest_framework.request import Request
from rest_framework.views import APIView
from django.http import JsonResponse

from modu_property.utils.loggers import logger

from real_estate.containers.search_container import SearchContainer
from real_estate.schema.manticore_view_schema import get_manticore_view_get_decorator
from dependency_injector.wiring import inject, Provide


class IndexSearchEngineView(APIView):
    @inject
    def __init__(
        self,
        search_client: SearchClientInterface = Provide[SearchContainer.search_client],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.search_client = search_client

    @get_manticore_view_get_decorator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        try:
            self.search_client.run_indexer()
            return JsonResponse(
                data={},
                status=200,
                safe=False,
            )
        except Exception as e:
            logger.error(f"celery -> django -> manticore e : {e}")
            return JsonResponse(
                data={},
                status=400,
                safe=False,
            )
