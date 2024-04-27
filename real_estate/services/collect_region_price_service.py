import threading
from datetime import datetime
from decimal import ROUND_UP, Decimal
from typing import List

from dependency_injector.wiring import Provide

from modu_property.utils.loggers import logger
from modu_property.utils.time import TimeUtil
from real_estate.containers.repository_container import RepositoryContainer
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.models import Deal, RealEstate
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.utils.env_util import EnvUtil
from real_estate.utils.get_collecting_period_util import GetCollectingPeriodUtil


class CollectRegionPriceService:
    def __init__(
        self,
        real_estate_repository: RealEstateRepository = Provide[
            RepositoryContainer.repository
        ],
    ) -> None:
        self.real_estate_repository = real_estate_repository
        self.deal_types = [DealTypesForDBEnum.DEAL.value]

    def execute(self, sido, start_date, end_date):

        years_and_months = None
        if not all([start_date, end_date]):
            last_region_price = (
                self.real_estate_repository.get_last_region_price()
            )
            if not last_region_price:
                raise Exception(
                    "시작/종료 연월과 region_price 둘 다 없음. 둘 중에 하나는 있어야 함"
                )

            years_and_months = GetCollectingPeriodUtil.get_collecting_period(
                instance=last_region_price
            )
        else:
            years_and_months = GetCollectingPeriodUtil.get_collecting_period(
                start_date=start_date, end_date=end_date
            )

        regions = self.real_estate_repository.get_regions(sido=sido)
        if not regions:
            logger.error("regions not found")
            return

        existing_region_price_dict: dict[str, None] = (
            self.create_existing_region_price_dict()
        )

        for year_and_month in years_and_months:
            for region in regions:
                deal_year, deal_month = TimeUtil.split_year_and_month(
                    year_and_month=year_and_month
                )

                if self._skip_alreay_region_price_existing(
                    region=region,
                    deal_year=deal_year,
                    deal_month=deal_month,
                    existing_region_price_dict=existing_region_price_dict,
                ):
                    continue

                self.collect_region_price(
                    deal_year=deal_year,
                    deal_month=deal_month,
                    region=region,
                )

    def create_existing_region_price_dict(self) -> dict[str, None]:
        """
        region_price에 deal_date, region_id가 있으면 제외
        key -> region-id-year-month
        """
        region_prices_dict = {}
        region_prices = self.real_estate_repository.get_region_prices()
        if not region_prices:
            logger.error(f"region_prices not found")
            return region_prices_dict

        region_prices = list(region_prices)
        for region_price in region_prices:
            deal_date = datetime.strftime(region_price.deal_date, "%Y%m%d")
            deal_year, deal_month = TimeUtil.split_year_and_month(
                year_and_month=deal_date
            )

            region_price_key = self.create_region_price_key(
                region_id=region_price.region_id,
                deal_year=deal_year,
                deal_month=deal_month,
            )

            region_prices_dict[region_price_key] = None
        return region_prices_dict

    def create_region_price_key(
        self, region_id: int, deal_year: str, deal_month: str
    ) -> str:
        return f"{region_id}-{deal_year}-{deal_month}"

    def _skip_alreay_region_price_existing(
        self, region, deal_year, deal_month, existing_region_price_dict
    ):
        region_price_key = self._create_region_price_key(
            region_id=region.id, deal_year=deal_year, deal_month=deal_month
        )

        if region_price_key in existing_region_price_dict:
            return True

    def _create_region_price_key(
        self, region_id: int, deal_year: str, deal_month: str
    ) -> str:
        return f"{region_id}-{deal_year}-{deal_month}"

    def collect_region_price(self, deal_year, deal_month, region) -> bool:
        """
        real_estate.address에 시~리 있는거 가져오기
        real_estate.deals에서 deal 연월에 해당하는거 가져오기
        개수 세기
        매매 총 거래액, 총 평당가
        전세 총 거래액, 총 평당가
        """
        threads = []
        for deal_type in self.deal_types:
            dto: CollectRegionPriceDto = CollectRegionPriceDto(
                region=region,
                deal_type=deal_type,
                deal_year=deal_year,
                deal_month=deal_month,
                is_deal_canceled=False,
            )
            if EnvUtil.not_test_env():
                t = threading.Thread(
                    target=self._collect_region_price, args=(dto,)
                )
                t.start()
                threads.append(t)
            else:
                self._collect_region_price(dto=dto)

        if EnvUtil.not_test_env():
            for _thread in threads:
                _thread.join()

    def _collect_region_price(self, dto):
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

    def set_deal_date(self, dto: CollectRegionPriceDto):
        dto.deal_date = datetime.strftime(
            datetime.strptime(
                f"{dto.deal_year}-{dto.deal_month}-01", "%Y-%m-%d"
            ),
            "%Y-%m-%d",
        )

    def calc_jeonse_price_per_pyung(self, dto: CollectRegionPriceDto):
        dto.average_jeonse_price_per_pyung = str(
            Decimal(
                Decimal(str(dto.total_jeonse_price_per_pyung))
                / dto.jeonse_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.jeonse_count
            else Decimal(0)
        )

    def calc_average_deal_price_per_pyung(self, dto: CollectRegionPriceDto):
        dto.average_deal_price_per_pyung = str(
            Decimal(
                Decimal(str(dto.total_deal_price_per_pyung)) / dto.deal_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.deal_count
            else Decimal(0)
        )

    def calc_average_jeonse_price(self, dto: CollectRegionPriceDto):
        dto.average_jeonse_price = str(
            Decimal(
                Decimal(str(dto.total_jeonse_price)) / dto.jeonse_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.jeonse_count
            else Decimal(0)
        )

    def calc_average_deal_price(self, dto: CollectRegionPriceDto):
        dto.average_deal_price = str(
            Decimal(
                Decimal(str(dto.total_deal_price)) / dto.deal_count
            ).quantize(Decimal(".00"), rounding=ROUND_UP)
            if dto.deal_count
            else Decimal(0)
        )

    def to_string(self, dto: CollectRegionPriceDto):
        dto.total_deal_price_per_pyung = str(dto.total_deal_price_per_pyung)
        dto.total_jeonse_price_per_pyung = str(dto.total_jeonse_price_per_pyung)

    def calc_prices(self, dto: CollectRegionPriceDto, real_estates):
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
            dto.target_region = f"{dto.region.sido} {dto.region.sigungu} {dto.region.ubmyundong}"
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
