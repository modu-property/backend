from dependency_injector import containers, providers
from real_estate.utils.address_converter import KakaoAddressConverter


class AddressConverterContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    address_converter = providers.Singleton(provides=KakaoAddressConverter)


AddressConverterContainer().wire(
    modules=[
        "real_estate.utils.address_collector",
    ]
)
