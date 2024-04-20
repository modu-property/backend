from dependency_injector import containers, providers
from manticore.manticore_client import ManticoreClient


class SearchContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    search_client = providers.Factory(provides=ManticoreClient)


SearchContainer().wire(
    modules=[
        "real_estate.views.manticore_view",
    ]
)
