from dependency_injector import containers, providers

from manticore.manticore_client import ManticoreClient
from real_estate.containers.search_container import SearchContainer
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.get_real_estates import (
    GetRealEstates,
    GetRegions,
)
from real_estate.serializers import (
    GetRealEstatesOnSearchResponseSerializer,
    GetRegionsOnSearchResponseSerializer,
)
from real_estate.services.search_real_estates import SearchRealEstates
from real_estate.services.set_real_estates import SetRealEstates


class RepositoryContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository = providers.Singleton(provides=RealEstateRepository)


class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository: providers.Singleton[RealEstateRepository] = (
        RepositoryContainer().repository
    )

    get_real_estates = providers.Factory(provides=GetRealEstates, repository=repository)
    get_regions = providers.Factory(provides=GetRegions, repository=repository)

    set_real_estate_real_estates = providers.Factory(
        provides=SetRealEstates,
        serializer=GetRealEstatesOnSearchResponseSerializer,
        key="real_estates",
    )
    set_real_estate_regions = providers.Factory(
        provides=SetRealEstates,
        serializer=GetRegionsOnSearchResponseSerializer,
        key="regions",
    )

    search_client: providers.Factory[ManticoreClient] = SearchContainer.search_client
    search_real_estates = providers.Singleton(
        provides=SearchRealEstates,
        search_client=search_client,
    )


ServiceContainer().wire(
    modules=[
        "real_estate.services.get_real_estates_on_map_service",
        "real_estate.services.get_real_estates_on_search_service",
    ]
)
