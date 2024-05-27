from dependency_injector import containers, providers

from manticore.manticore_client import ManticoreClient
from real_estate.containers.repository_container import RepositoryContainer
from real_estate.containers.search_container import SearchContainer
from real_estate.containers.utils.address_collector_container import (
    AddressCollectorContainer,
)
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_region_service import CollectRegionService
from real_estate.services.get_real_estates_service import (
    GetRealEstatesService,
    GetRegionsService,
)
from real_estate.serializers import (
    GetRealEstatesOnSearchResponseSerializer,
    GetRegionsOnSearchResponseSerializer,
)
from real_estate.services.insert_address_service import InsertRegionsService
from real_estate.services.search_real_estates_service import (
    SearchRealEstatesService,
)
from real_estate.services.set_real_estates_service import SetRealEstatesService


class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository: providers.Singleton[RealEstateRepository] = (
        RepositoryContainer().repository
    )

    get_real_estates = providers.Factory(
        provides=GetRealEstatesService, repository=repository
    )
    get_regions = providers.Factory(
        provides=GetRegionsService, repository=repository
    )

    set_real_estate_real_estates = providers.Factory(
        provides=SetRealEstatesService,
        serializer=GetRealEstatesOnSearchResponseSerializer,
        key="real_estates",
    )
    set_real_estate_regions = providers.Factory(
        provides=SetRealEstatesService,
        serializer=GetRegionsOnSearchResponseSerializer,
        key="regions",
    )

    search_client: providers.Factory[ManticoreClient] = (
        SearchContainer.search_client
    )
    search_real_estates = providers.Singleton(
        provides=SearchRealEstatesService,
        search_client=search_client,
    )

    insert_regions_service = providers.Factory(InsertRegionsService)

    collect_regions_service = providers.Factory(
        CollectRegionService,
        address_collector=AddressCollectorContainer.address_collector,
        repository=repository,
    )


ServiceContainer().wire(
    modules=[
        "real_estate.services.get_real_estates_on_map_service",
        "real_estate.services.get_real_estates_on_search_service",
        "real_estate.management.commands.insert_regional_code_command",
        "real_estate.management.commands.collect_regional_code_command",
    ]
)
