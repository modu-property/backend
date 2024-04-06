from typing import List, Union
from real_estate.models import Region
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.utils.address_collector import AddressCollector


class CollectRegionService:
    def __init__(
        self,
    ) -> None:
        self.address_collector = AddressCollector()
        self.real_estate_repository = RealEstateRepository()

    def collect(self) -> bool:
        regions: Union[List[Region], bool] = self.address_collector.collect_region()

        if not regions:
            return False

        return True
