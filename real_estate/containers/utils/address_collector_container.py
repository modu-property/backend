from dependency_injector import containers, providers

from real_estate.containers.utils.address_converter_container import (
    AddressConverterContainer,
)
from real_estate.utils.address_collector import AddressCollector
from real_estate.utils.address_converter import KakaoAddressConverter


class AddressCollectorContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    address_converter: providers.Singleton[KakaoAddressConverter] = (
        AddressConverterContainer.address_converter
    )

    address_collector = providers.Factory(
        provides=AddressCollector,
        address_converter=address_converter,
    )


AddressCollectorContainer().wire(
    modules=[
        "real_estate.utils.address_collector",
        "real_estate.services.collect_address_service",
    ]
)
