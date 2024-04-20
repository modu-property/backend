from dependency_injector import containers, providers

from real_estate.containers.repository_container import RepositoryContainer
from real_estate.containers.utils.address_converter_container import (
    AddressConverterContainer,
)
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.utils.address_collector import AddressCollector
from real_estate.utils.address_converter import KakaoAddressConverter


class AddressCollectorContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository: providers.Singleton[RealEstateRepository] = (
        RepositoryContainer.repository
    )

    address_converter: providers.Singleton[KakaoAddressConverter] = (
        AddressConverterContainer.address_converter
    )

    address_collector = providers.Factory(
        provides=AddressCollector,
        real_estate_repository=repository,
        address_converter=address_converter,
    )


AddressCollectorContainer().wire(
    modules=[
        "real_estate.utils.address_collector",
        "real_estate.services.collect_address_service",
    ]
)
