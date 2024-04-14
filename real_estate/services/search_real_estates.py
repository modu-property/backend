from dependency_injector.wiring import inject, Provide

from manticore.manticore_client import SearchClientInterface
from real_estate.containers.search_container import SearchContainer
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnSearchDto


class SearchRealEstates:
    @inject
    def __init__(
        self,
        search_client: SearchClientInterface = Provide[SearchContainer.search_client],
    ) -> None:
        self.search_client: SearchClientInterface = search_client

    def search(self, dto: GetRealEstatesOnSearchDto, index: str = "") -> list:
        real_estates = []
        query = {"query_string": f"@* *{dto.keyword}*"}

        self._set_region_count_limit(dto=dto)

        hits = self.search_client.search(index=index, query=query, limit=dto.limit)

        for hit in hits:
            real_estate_info = hit["_source"]
            real_estate_id = int(hit["_id"])
            real_estate_info["id"] = real_estate_id
            real_estates.append(real_estate_info)

        return real_estates

    def _set_region_count_limit(self, dto: GetRealEstatesOnSearchDto) -> None:
        dto.limit = 3
