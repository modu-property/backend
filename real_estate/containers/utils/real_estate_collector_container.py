from PublicDataReader import TransactionPrice
from dependency_injector import containers, providers

from real_estate.containers.utils.third_party_container import (
    ThirdPartyContainer,
)
from real_estate.utils.real_estate_collector_util import RealEstateCollectorUtil


class RealEstateCollectorContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    transaction_price: providers.Singleton[TransactionPrice] = (
        ThirdPartyContainer.transaction_price
    )

    real_estate_collector = providers.Factory(
        provides=RealEstateCollectorUtil,
        transaction_price=transaction_price,
    )


RealEstateCollectorContainer().wire(
    modules=[
        "real_estate.services.collect_deal_price_of_real_estate_service",
    ]
)
