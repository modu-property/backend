from dependency_injector import containers, providers

from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.get_real_estates import (
    GetRealEstates,
    GetRegions,
)


class RepositoryContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    # wiring_config = containers.WiringConfiguration(
    #     modules=["real_estate.services.get_real_estates_on_map_service"]
    # )

    repository = providers.Singleton(RealEstateRepository)


class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        modules=["real_estate.services.get_real_estates_on_map_service"]
    )

    # repository = providers.Singleton(RealEstateRepository)
    repository = RepositoryContainer().repository

    get_real_estates = providers.Factory(provides=GetRealEstates, repository=repository)
    get_regions = providers.Factory(provides=GetRegions, repository=repository)


ServiceContainer().wire(
    modules=["real_estate.services.get_real_estates_on_map_service"]
)
