from dependency_injector import containers, providers

from real_estate.containers.search_container import SearchContainer
from real_estate.containers.service_container import ServiceContainer


class Container(containers.DeclarativeContainer):

    search_client = SearchContainer.search_client

    service_package = providers.Container(
        ServiceContainer,
        search_client=search_client,
    )


Container().wire(
    modules=[
        "real_estate.services.get_real_estates_on_search_service",
    ]
)
