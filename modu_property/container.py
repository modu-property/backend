from dependency_injector import containers, providers

from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.get_real_estates import (
    GetRealEstates,
    GetRealEstatesInterface,
)


class RepositoryContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository = providers.Singleton(RealEstateRepository)


class ServiceContainer(containers.DeclarativeContainer):
    # wiring_config = containers.WiringConfiguration(
    #     modules=["real_estate.services.get_real_estates_on_map_service"]
    # )

    repository = providers.DependenciesContainer()

    # get_real_estates = providers.Singleton(GetRealEstates)

    get_real_estates = providers.Factory(
        GetRealEstates, repository=RepositoryContainer.repository
    )

    # providers.Factory(GetRealEstatesInterface, get_real_estates=get_real_estates)
