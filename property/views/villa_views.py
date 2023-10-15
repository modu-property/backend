from typing import Union

from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
import pymysql
from rest_framework.request import Request
from rest_framework.views import APIView
from accounts.util.authenticator import jwt_authenticator
from manticore.manticore_client import ManticoreClient
from property.dto.villa_dto import GetDealPriceOfVillaDto

from property.models import Villa
from property.serializers import (
    GetVillaRequestSerializer,
    GetVillasOnSearchTabResponseSerializer,
)
from property.services.get_deal_price_of_villa_service import GetDealPriceOfVillaService

import manticoresearch


import manticoresearch
from manticoresearch.api import search_api
from manticoresearch.model.search_request import SearchRequest
from manticoresearch.model.error_response import ErrorResponse
from manticoresearch.model.search_response import SearchResponse
from manticoresearch.model.query_filter import QueryFilter
from pprint import pprint


class VillaView(APIView):
    @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Union[HttpResponse, HttpResponseNotFound]:
        # search tab에서 검색할 때 나오는 빌라 주소 정보

        # Defining the host is optional and defaults to http://127.0.0.1:9308
        # See configuration.py for a list of all supported configuration parameters.
        configuration = manticoresearch.Configuration(host="http://0.0.0.0:9308")

        # Enter a context with an instance of the API client
        with manticoresearch.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = search_api.SearchApi(api_client)

            search_request = SearchRequest(
                index="property_villa",
                query={"query_string": "연수동"},
            )

            try:
                # Performs a search
                api_response = api_instance.search(search_request)
                pprint(api_response)
                hits = api_response.hits
                hits = hits.hits
                villas = []
                for hit in hits:
                    source = hit["_source"]
                    villa = GetVillasOnSearchTabResponseSerializer(source)
                    villas.append(villa)
                    # TODO villa serializer 써서 응답해야 함
                return JsonResponse(data=villas)
            except manticoresearch.ApiException as e:
                print("Exception when calling SearchApi->search: %s\n" % e)
                return JsonResponse(data={})
            except Exception as e:
                print(f"e : {e}")
                return JsonResponse(data={})


###################################


# """
# TODO
# * 위경도+줌레벨, 검색어+줌레벨 받기
# * 검색어면 위경도로 변환
# * 위경도 기준으로 줌레벨에 맞는 반경 n킬로미터에 있는 빌라 매물 정보 가져오기

# postgresql 써야하나?
# mysql에 위경도로 거리 계산하는거 있는지 확인 필요!
# """
# request_data = {
#     "type": kwargs["type"],
#     "latitude": request.query_params["latitude"],
#     "longitude": request.query_params["longitude"],
#     "zoom_level": request.query_params["zoom_level"],
#     "keyword": request.query_params["keyword"],
# }
# serializer = GetVillaRequestSerializer(data=request_data)

# if serializer.is_valid():
#     validated_data = serializer.validated_data
#     dto = GetDealPriceOfVillaDto(**validated_data)
#     GetDealPriceOfVillaService().execute(dto=dto)

# manticore_client = ManticoreClient()
# body = (
#     "["
#     '{"insert": {"index": "test", "id": 1, "doc": {"title": "Title 1"}}},\\n{"insert": {"index": "test", "id": 2, "doc": {"title": "Title 2"}}}'
#     "]"
# )
# manticore_client.index(body=body)
# manticore_client.search(index="property_villa", query_string="연수동")

# return JsonResponse(data={})
# post_list = News.objects.all()

# serialized_news_list = NewsSerializer(post_list, many=True).data
# if not serialized_news_list:
#     return HttpResponseNotFound()
# return JsonResponse(serialized_news_list, safe=False)
