from dependency_injector import containers, providers
from real_estate.utils.address_converter import KakaoAddressConverter


class AddressConverterContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    address_converter = providers.Singleton(provides=KakaoAddressConverter)


AddressConverterContainer().wire(
    modules=[
        "real_estate.utils.address_collector",
        "real_estate.services.collect_deal_price_of_real_estate_service",
    ]
)
