from dependency_injector import containers, providers

from real_estate.utils.address_converter import KakaoAddressConverter


class UtilContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    address_converter = providers.Factory(provides=KakaoAddressConverter)


UtilContainer().wire(
    modules=[
        "real_estate.utils.address_collector",
    ]
)
