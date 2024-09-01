from abc import ABC, abstractmethod
import os
import subprocess
from typing import Any, Dict, List, Optional
from modu_property.utils.loggers import logger, file_logger
import manticoresearch

from manticoresearch.api import search_api
from manticoresearch.model.search_request import SearchRequest


class SearchClientInterface(ABC):
    @abstractmethod
    def run_indexer(self) -> None:
        pass

    @abstractmethod
    def search(
        self, index: str, query: dict, limit: int
    ) -> List[Optional[Dict[str, Any]]]:
        pass


class ManticoreClient(SearchClientInterface):
    def __init__(self) -> None:
        self.configuration = manticoresearch.Configuration(
            host=f"http://{os.getenv('HTTP_HOST')}:{os.getenv('HTTP_PORT')}"
        )
        self.api_client = manticoresearch.ApiClient(self.configuration)
        self.search_api = search_api.SearchApi(self.api_client)

    def run_indexer(self) -> None:
        logger.info("run_indexer")
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            sh_filename = (
                "run_indexer.sh"
                if os.getenv("SERVER_ENV") != "local"
                else "run_indexer_local.sh"
            )
            sh_path = f"{dir_path}/{sh_filename}"
            logger.info(f"sh_path : {sh_path}")
            subprocess.run(["bash", sh_path])
        except Exception as e:
            logger.error(f"ManticoreClient run_indexer e : {e}")

    def search(
        self, index: str, query: dict, limit: int
    ) -> List[Optional[Dict[str, Any]]]:
        try:
            file_logger.info(f"search query : {query}")
            search_request = SearchRequest(
                index=index, query=query, limit=limit
            )

            search_response = self.search_api.search(search_request)
            hits = search_response.hits
            file_logger.info(f"search hits : {hits}")
            if not hits:
                return []
            hits = hits.hits
            file_logger.info(f"search hits : {hits}")
            return hits
        except Exception as e:
            logger.error(f"ManticoreClient search e : {e}")
            return []
