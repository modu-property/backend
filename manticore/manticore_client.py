import os
import subprocess
from modu_property.utils.loggers import logger
import manticoresearch
import manticoresearch

from manticoresearch.api import search_api
from manticoresearch.model.search_request import SearchRequest


class ManticoreClient:
    def __init__(self) -> None:
        self.configuration = manticoresearch.Configuration(
            host=f"http://{os.getenv('HTTP_HOST')}:{os.getenv('HTTP_PORT')}"
        )
        self.api_client = manticoresearch.ApiClient(self.configuration)
        self.search_instance = search_api.SearchApi(self.api_client)

    def run_indexer(self):
        logger.info("run_indexer")
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            subprocess.run(["bash", f"{dir_path}/run_indexer.sh"])
        except Exception as e:
            logger.error(f"ManticoreClient run_indexer e : {e}")

    def search(self, index: str, query: dict, limit: int):
        try:
            search_request = SearchRequest(index=index, query=query, limit=limit)

            search_response = self.search_instance.search(search_request)
            hits = search_response.hits
            if not hits:
                return []
            hits = hits.hits
            return hits
        except Exception as e:
            logger.error(f"ManticoreClient search e : {e}")
            return []
