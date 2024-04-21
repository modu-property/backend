from dependency_injector import containers, providers

from real_estate.utils.paginator_util import PaginatorUtil


class PaginatorContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    paginator = providers.Singleton(provides=PaginatorUtil)


PaginatorContainer().wire(
    modules=[
        "real_estate.services.get_deals_service",
    ]
)
