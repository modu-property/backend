from typing import List, Union
from real_estate.containers.utils.address_collector_container import (
    AddressCollectorContainer,
)
from real_estate.models import Region
from real_estate.utils.address_collector import AddressCollector

from dependency_injector.wiring import inject, Provide


class CollectRegionService:
    @inject
    def __init__(
        self, address_collector=Provide[AddressCollectorContainer.address_collector]
    ) -> None:
        self.address_collector: AddressCollector = address_collector

    def collect_region(self) -> bool:
        regions: Union[List[Region], bool] = self.address_collector.collect_region()

        if not regions:
            return False

        return True
