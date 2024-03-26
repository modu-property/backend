from datetime import datetime
from decimal import ROUND_UP, Decimal
from typing import List

from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.models import Deal, RealEstate
from real_estate.repository.real_estate_repository import RealEstateRepository


class CollectRegionPriceService:
    def __init__(
        self,
    ) -> None:
        self.real_estate_repository = RealEstateRepository()

    def execute(self, dto: CollectRegionPriceDto) -> bool:
        """
        real_estate.address에 시~리 있는거 가져오기
        real_estate.deals에서 deal 연월에 해당하는거 가져오기
        개수 세기
        매매 총 거래액, 총 평당가
        전세 총 거래액, 총 평당가
        """
        self.set_target_region(dto=dto)
        real_estates: List[RealEstate] = list(
            self.real_estate_repository.get_real_estates(dto=dto)
        )

        if not real_estates:
            return False

        self.set_deal_date(dto)
        self.calc_prices(dto, real_estates)
        self.to_string(dto)
        self.calc_average_deal_price(dto)
        self.calc_average_jeonse_price(dto)
        self.calc_average_deal_price_per_pyung(dto)
        self.calc_jeonse_price_per_pyung(dto)

        region_price = self.real_estate_repository.create_region_price(dto=dto)
        return region_price

    def set_deal_date(self, dto):
        dto.deal_date = datetime.strftime(
            datetime.strptime(f"{dto.deal_year}-{dto.deal_month}-01", "%Y-%m-%d"),
            "%Y-%m-%d",
        )

    def calc_jeonse_price_per_pyung(self, dto):
        dto.average_jeonse_price_per_pyung = str(
            Decimal(
                Decimal(str(dto.total_jeonse_price_per_pyung)) / dto.jeonse_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.jeonse_count
            else Decimal(0)
        )

    def calc_average_deal_price_per_pyung(self, dto):
        dto.average_deal_price_per_pyung = str(
            Decimal(
                Decimal(str(dto.total_deal_price_per_pyung)) / dto.deal_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.deal_count
            else Decimal(0)
        )

    def calc_average_jeonse_price(self, dto):
        dto.average_jeonse_price = str(
            Decimal(Decimal(str(dto.total_jeonse_price)) / dto.jeonse_count).quantize(
                Decimal(".00"), rounding=ROUND_UP
            )
            if dto.jeonse_count
            else Decimal(0)
        )

    def calc_average_deal_price(self, dto):
        dto.average_deal_price = str(
            Decimal(Decimal(str(dto.total_deal_price)) / dto.deal_count).quantize(
                Decimal(".00"), rounding=ROUND_UP
            )
            if dto.deal_count
            else Decimal(0)
        )

    def to_string(self, dto):
        dto.total_deal_price_per_pyung = str(dto.total_deal_price_per_pyung)
        dto.total_jeonse_price_per_pyung = str(dto.total_jeonse_price_per_pyung)

    def calc_prices(self, dto, real_estates):
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

    def set_target_region(self, dto: CollectRegionPriceDto):
        if dto.region.sido:
            self.filter_sido(dto=dto)
        if dto.region.dongri:
            dto.target_region = f"{dto.region.sido} {dto.region.sigungu} {dto.region.ubmyundong} {dto.region.dongri}"
        elif dto.region.ubmyundong:
            dto.target_region = (
                f"{dto.region.sido} {dto.region.sigungu} {dto.region.ubmyundong}"
            )
        elif dto.region.sigungu:
            dto.target_region = f"{dto.region.sido} {dto.region.sigungu}"
        elif dto.region.sido:
            dto.target_region = dto.region.sido

    def filter_sido(self, dto: CollectRegionPriceDto):
        sido: str = dto.region.sido
        if "특별시" in sido:
            dto.region.sido = "서울"
        elif "광역시" in sido:
            dto.region.sido = sido[2:]
        elif "남도" in sido or "북도" in sido:
            dto.region.sido = sido[0] + sido[2]
        elif "경기도" in sido:
            dto.region.sido = "경기"
        elif "특별" in sido:
            pass
