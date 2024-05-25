from dependency_injector import containers, providers

from real_estate.containers.utils.address_converter_container import (
    AddressConverterContainer,
)
from real_estate.utils.address_collector_util import AddressCollectorUtil
from real_estate.utils.address_converter_util import KakaoAddressConverterUtil


class AddressCollectorContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    address_converter_util: providers.Singleton[KakaoAddressConverterUtil] = (
        AddressConverterContainer.address_converter
    )

    address_collector = providers.Factory(
        provides=AddressCollectorUtil,
        address_converter_util=address_converter_util,
    )


AddressCollectorContainer().wire(
    modules=[
        "real_estate.utils.address_collector_util",
        "real_estate.services.collect_region_service",
    ]
)
