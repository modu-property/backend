from dependency_injector import containers, providers

from real_estate.repository.real_estate_repository import RealEstateRepository


class RepositoryContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository = providers.Singleton(provides=RealEstateRepository)


RepositoryContainer().wire(
    modules=[
        "real_estate.utils.address_collector_util",
        "real_estate.services.collect_region_price_service",
        "real_estate.services.get_deals_service",
        "real_estate.services.collect_address_service",
        "real_estate.management.commands.collect_command_mixin",
        "real_estate.services.calc_region_price_service",
    ]
)
