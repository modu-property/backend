from manticore.manticore_client import ManticoreClient

from rest_framework.request import Request
from rest_framework.views import APIView
from django.http import JsonResponse

from modu_property.utils.loggers import logger
from real_estate.schema.manticore_view_schema import get_manticore_view_get_decorator


class ManticoreView(APIView):
    @get_manticore_view_get_decorator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> JsonResponse:
        logger.info("ManticoreView")

        try:
            manticore = ManticoreClient()
            manticore.run_indexer()
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
