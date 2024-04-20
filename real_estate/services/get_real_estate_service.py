from typing import Any, Optional
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetRealEstateDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.models import RealEstate
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import GetRealEstateResponseSerializer


class GetRealEstateService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def get_real_estate(self, dto: GetRealEstateDto) -> ServiceResultDto:
        real_estate: Optional[RealEstate] = self.repository.get_real_estate(
            id=dto.id
        )

        if not real_estate:
            return ServiceResultDto(status_code=404)

        data: Any = validate_data(
            serializer=GetRealEstateResponseSerializer,
            queryset=real_estate,
        )
        if not data:
            return ServiceResultDto(
                message="GetRealEstateResponseSerializer 에러", status_code=400
            )
        return ServiceResultDto(data=data)
