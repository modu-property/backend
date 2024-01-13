import json
import os
import subprocess
from modu_property.utils.loggers import logger
import manticoresearch
from manticoresearch.api import index_api
from manticoresearch.model.bulk_response import BulkResponse
from manticoresearch.model.error_response import ErrorResponse


class ManticoreClient:
    def __init__(self) -> None:
        self.configuration = manticoresearch.Configuration(host="http://0.0.0.0:9308")

    def run_indexer(self):
        logger.info("run_indexer")

        # with manticoresearch.ApiClient(self.configuration) as api_client:
        #     api_instance = index_api.IndexApi(api_client)

        # body = (
        #     "["
        #     '{"insert": {"index": "real_estate", "doc": {"lot_number": "Title 1", "road_name_address": "asdf", "name": "name1"}}},{"insert": {"index": "real_estate", "doc": {"title": "Title 2", "road_name_address": "aaaa", "name": "name2"}}}'
        #     "]"
        # )  # str
        # body_list = [
        #     {
        #         "insert": {
        #             "index": "real_estate",
        #             "doc": {
        #                 "lot_number": "Title 1",
        #                 "road_name_address": "asdf",
        #                 "name": "name1",
        #             },
        #         }
        #     },
        #     {
        #         "insert": {
        #             "index": "real_estate",
        #             "doc": {
        #                 "title": "Title 2",
        #                 "road_name_address": "aaaa",
        #                 "name": "name2",
        #             },
        #         }
        #     },
        # ]
        # body = {
        #     "insert": {
        #         "index": "real_estate",
        #         "doc": {
        #             "id": 1,
        #             "lot_number": "Title 1",
        #             "road_name_address": "asdf",
        #             "name": "name1",
        #         },
        #     }
        # }
        # # body_list = "\n".join(map(json.dumps, body_list))

        # # example passing only required values which don't have defaults set
        # try:
        #     # Bulk index operations
        #     # api_response = api_instance.bulk(body_list)
        #     api_response = api_instance.insert(body)
        #     logger.info(api_response)
        # except manticoresearch.ApiException as e:
        #     print("Exception when calling IndexApi->bulk: %s\n" % e)
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            subprocess.run(["bash", f"{dir_path}/run_indexer.sh"])
        except Exception as e:
            logger.error(f"run_indexer e : {e}")


# from __future__ import print_function

# import manticoresearch
# from manticoresearch import SearchRequest, QueryFilter
# from manticoresearch.rest import ApiException


# import time
# import manticoresearch
# from manticoresearch import *
# from manticoresearch.rest import ApiException
# from pprint import pprint

# from property.models import Villa


# class ManticoreClient:
#     def __init__(self) -> None:
#         configuration = manticoresearch.Configuration(host="http://127.0.0.1:9308")
#         api_client = manticoresearch.ApiClient(configuration)
#         self.index_api = manticoresearch.IndexApi(api_client)
#         self.search_api = manticoresearch.SearchApi(api_client)

#     def index(self, body: str):
#         try:
#             req_body = {
#                 "index": "property_villa",
#                 "doc": {
#                     "dong": "논현동",
#                     "lot_number": "234-2",
#                     "road_name_address": "서울시 서초구 주흥길 1-1",
#                 },
#             }

#             villa = Villa.objects.all()[0]

#             api_resp = self.index_api.insert(req_body)
#             # response = self.index_api.bulk(body)
#             print(api_resp)
#         except ApiException as e:
#             print("Exception when calling IndexApi->bulk: %s\n" % e)

#     def search(self, index: str, query_string: str):
#         search_request = SearchRequest()
#         search_request.index = index
#         search_request.fulltext_filter = QueryFilter(query_string=query_string)

#         try:
#             response = self.search_api.search(search_request=search_request)
#             print(response)
#             pass
#         except ApiException as e:
#             print("Exception when calling SearchApi->search: %s\n" % e)


# # Defining the host is optional and defaults to http://127.0.0.1:9308
# # See configuration.py for a list of all supported configuration parameters.
# # configuration = manticoresearch.Configuration(host="http://127.0.0.1:9308")


# # # Enter a context with an instance of the API client
# # with manticoresearch.ApiClient(configuration) as api_client:
# #     # Create an instance of the IndexApi API class
# #     api_instance = manticoresearch.IndexApi(api_client)
# #     body = (
# #         "[" '{"insert": {"index": "test", "id": 1, "doc": {"title": "Title 1"}}}' "]"
# #     )  # str |

# #     try:
# #         # Bulk index operations
# #         api_response = api_instance.bulk(body)
# #         pprint(api_response)
# #     except ApiException as e:
# #         print("Exception when calling IndexApi->bulk: %s\n" % e)

# #     # Create an instance of the Search API class
# #     api_instance = manticoresearch.SearchApi(api_client)

# #     # Create SearchRequest
# #     search_request = SearchRequest()
# #     search_request.index = "test"
# #     search_request.fullltext_filter = QueryFilter("Title 1")

# #     # The example passes only required values which don't have defaults set
# #     try:
# #         # Perform a search
# #         api_response = api_instance.search(search_request)
# #         pprint(api_response)
# #     except manticoresearch.ApiException as e:
# #         print("Exception when calling SearchApi->search: %s\n" % e)
