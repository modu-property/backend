from typing import List, Union

from modu_property.utils.loggers import logger
from real_estate.containers.repository_container import RepositoryContainer
from real_estate.containers.utils.address_collector_container import (
    AddressCollectorContainer,
)
from real_estate.models import Region
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.utils.address_collector_util import AddressCollectorUtil

from dependency_injector.wiring import inject, Provide


class CollectRegionService:
    @inject
    def __init__(
        self,
        address_collector=Provide[AddressCollectorContainer.address_collector],
        repository: RealEstateRepository = Provide[
            RepositoryContainer.repository
        ],
    ) -> None:
        self.address_collector: AddressCollectorUtil = address_collector
        self.repository: RealEstateRepository = repository

    def collect_region(self) -> bool:
        logger.info("collect_region start")
        region_models: Union[List[Region], bool] = (
            self.address_collector.collect_region()
        )

        if not region_models:
            return False

        result: Union[List[Region], bool] = self.repository.bulk_create_regions(
            region_models=region_models
        )
        logger.info("collect_region finish")

        return result
