from decimal import Decimal, ROUND_UP

from dependency_injector.wiring import Provide, inject

from modu_property.utils.time import TimeUtil
from real_estate.containers.repository_container import RepositoryContainer
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.models import Deal
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.set_target_region_service import (
    SetTargetRegionService,
)


class CalcRegionPriceService:
    @inject
    def __init__(
        self,
        real_estate_repository: RealEstateRepository = Provide[
            RepositoryContainer.repository
        ],
    ) -> None:
        self.real_estate_repository = real_estate_repository

    def calc_region_price(self, dto):
        SetTargetRegionService.set_target_region(dto=dto)
        real_estates = self._get_real_estates(dto=dto)
        if not real_estates:
            return False

        dto.deal_date = TimeUtil.get_deal_date(
            deal_year=dto.deal_year, deal_month=dto.deal_month
        )
        self._calc_prices(dto, real_estates)
        self._convert_decimal_to_str(dto)
        self._calc_average_deal_price(dto)
        self._calc_average_jeonse_price(dto)
        self._calc_average_deal_price_per_pyung(dto)
        self._calc_jeonse_price_per_pyung(dto)
        region_price = self.real_estate_repository.create_region_price(dto=dto)
        return region_price

    def _get_real_estates(self, dto):
        return list(self.real_estate_repository.get_real_estates(dto=dto))

    @staticmethod
    def _calc_jeonse_price_per_pyung(dto: CollectRegionPriceDto):
        dto.average_jeonse_price_per_pyung = str(
            Decimal(
                Decimal(str(dto.total_jeonse_price_per_pyung))
                / dto.jeonse_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.jeonse_count
            else Decimal(0)
        )

    @staticmethod
    def _calc_average_deal_price_per_pyung(dto: CollectRegionPriceDto):
        dto.average_deal_price_per_pyung = str(
            Decimal(
                Decimal(str(dto.total_deal_price_per_pyung)) / dto.deal_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.deal_count
            else Decimal(0)
        )

    @staticmethod
    def _calc_average_jeonse_price(dto: CollectRegionPriceDto):
        dto.average_jeonse_price = str(
            Decimal(
                Decimal(str(dto.total_jeonse_price)) / dto.jeonse_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.jeonse_count
            else Decimal(0)
        )

    @staticmethod
    def _calc_average_deal_price(dto: CollectRegionPriceDto):
        dto.average_deal_price = str(
            Decimal(
                Decimal(str(dto.total_deal_price)) / dto.deal_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.deal_count
            else Decimal(0)
        )

    @staticmethod
    def _convert_decimal_to_str(dto: CollectRegionPriceDto):
        dto.total_deal_price_per_pyung = str(dto.total_deal_price_per_pyung)
        dto.total_jeonse_price_per_pyung = str(dto.total_jeonse_price_per_pyung)

    @staticmethod
    def _calc_prices(dto: CollectRegionPriceDto, real_estates):
        for real_estate in real_estates:
            deals: list[Deal] = list(real_estate.deals.all())
            for deal in deals:
                if deal.deal_type == DealTypesForDBEnum.DEAL.value:
                    dto.total_deal_price += deal.deal_price
                    dto.total_deal_price_per_pyung += Decimal(
                        str(deal.area_for_exclusive_use_price_per_pyung)
                    )

                    dto.deal_count += 1

                elif deal.deal_type == DealTypesForDBEnum.JEONSE.value:
                    dto.total_jeonse_price += deal.deal_price
                    dto.total_jeonse_price_per_pyung += Decimal(
                        str(deal.area_for_exclusive_use_price_per_pyung)
                    )

                    dto.jeonse_count += 1
