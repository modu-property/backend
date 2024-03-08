import logging

from real_estate.dto.get_real_estate_dto import GetDealsDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.deal_enum import DealPerPageEnum
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.serializers import (
    DealSerializer,
    GetDealsResponseSerializer,
)
from django.core.paginator import Paginator, Page


class GetDealsService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def execute(self, dto: GetDealsDto) -> ServiceResultDto:
        deals = self.repository.get_deals(dto=dto)

        per_page = DealPerPageEnum.PER_PAGE.value
        paginator = Paginator(deals, per_page)
        total_page_info: Page = paginator.get_page(dto.page)
        total_pages = total_page_info.paginator.num_pages

        current_page = total_page_info.number
        deals = total_page_info.object_list

        validated_deals = DealSerializer(
            deals,
            many=True,
        ).data
        deals_list = [dict(deal) for deal in validated_deals]

        data = {
            "deals": deals_list,
            "current_page": current_page,
            "total_pages": total_pages,
        }
        serializer = GetDealsResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            return ServiceResultDto(data=serializer.validated_data)
        except Exception as e:
            logging.error(f"e : {e}")
            return ServiceResultDto(
                status_code=400, message="GetDealsResponseSerializer error"
            )
