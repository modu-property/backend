from dependency_injector import containers, providers
from real_estate.services.search_real_estates import SearchRealEstates


class SearchRealEstatesContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # search_container = SearchContainer

    search_client = providers.Dependency()

    search_real_estates = providers.Factory(
        provides=SearchRealEstates, search_client=search_client
    )


SearchRealEstatesContainer().wire(
    modules=[
        "real_estate.services.get_real_estates_on_search_service",
    ]
)
