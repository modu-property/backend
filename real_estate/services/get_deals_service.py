from dependency_injector.wiring import Provide, inject
from django.db.models import QuerySet

from real_estate.containers.repository_container import RepositoryContainer
from real_estate.dto.get_real_estate_dto import GetDealsDto
from real_estate.models import Deal
from real_estate.repository.real_estate_repository import RealEstateRepository


class GetDealsService:
    @inject
    def __init__(
        self,
        repository: RealEstateRepository = Provide[
            RepositoryContainer.repository
        ],
    ) -> None:
        self.repository = repository

    def get_deals(self, dto: GetDealsDto) -> QuerySet[Deal]:
        deals = self.repository.get_deals(dto=dto)
        return deals
