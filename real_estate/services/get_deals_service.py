import logging

from real_estate.dto.get_real_estate_dto import GetDealsDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import DealSerializer


class GetDealsService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def execute(self, dto: GetDealsDto) -> ServiceResultDto:
        deals = self.repository.get_deals(dto=dto)

        try:
            deals = DealSerializer(
                deals,
                many=True,
            ).data

            return ServiceResultDto(data=deals)
        except Exception as e:
            logging.error(f"e : {e}")
            return ServiceResultDto(status_code=400, message="DealSerializer error")
