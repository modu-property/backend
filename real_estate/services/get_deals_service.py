import logging

from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetDealsDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.deal_enum import DealPerPageEnum
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import (
    DealSerializer,
    GetDealsResponseSerializer,
)
from real_estate.utils.paginator import PaginatorUtil


class GetDealsService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()
        self.paginator = PaginatorUtil()

    def execute(self, dto: GetDealsDto) -> ServiceResultDto:
        deals = self.repository.get_deals(dto=dto)

        deals, total_pages, current_page = self.paginator.get_page_info(
            current_page=dto.page,
            object_list=deals,
            per_page=DealPerPageEnum.PER_PAGE.value,
        )

        deals_list = self.create_deal_list(deals)

        data = {
            "deals": deals_list,
            "current_page": current_page,
            "total_pages": total_pages,
        }
        data = validate_data(serializer=GetDealsResponseSerializer, data=data)

        try:
            return ServiceResultDto(data=data)
        except Exception as e:
            logging.error(f"e : {e}")
            return ServiceResultDto(
                status_code=400, message="GetDealsResponseSerializer error"
            )

    def create_deal_list(self, deals):
        deals_list = []
        if deals:
            validated_deals = validate_data(
                serializer=DealSerializer, queryset=deals, many=True
            )
            deals_list = [dict(deal) for deal in validated_deals]
        return deals_list
