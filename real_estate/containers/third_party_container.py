import os
from dependency_injector import containers, providers

from PublicDataReader import TransactionPrice


class ThirdPartyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    transaction_price = providers.Singleton(
        provides=TransactionPrice, service_key=os.getenv("SERVICE_KEY")
    )


ThirdPartyContainer().wire(
    modules=[
        "real_estate.utils.address_collector",
    ]
)
