import threading
from datetime import datetime
from typing import List

from dependency_injector.wiring import Provide

from modu_property.utils.loggers import logger
from modu_property.utils.time import TimeUtil
from real_estate.containers.repository_container import RepositoryContainer
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from real_estate.models import Region
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.calc_region_price_service import (
    CalcRegionPriceService,
)
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

    def collect_region_price_within_period(self, sido, start_date, end_date):
        regions = self.real_estate_repository.get_regions(sido=sido)
        self._check_region_exist(regions)

        years_and_months = self._get_years_and_months(end_date, start_date)
        self._collect_region_price_by_date_and_region(
            years_and_months,
            regions,
        )

    @staticmethod
    def _check_region_exist(regions):
        if not regions:
            raise Exception("regions not found")

    def _get_years_and_months(self, end_date, start_date) -> List[str]:
        if not all([start_date, end_date]):
            last_region_price = (
                self.real_estate_repository.get_last_region_price()
            )
            if not last_region_price:
                raise Exception(
                    "시작/종료 연월과 region_price 둘 다 없음. 둘 중에 하나는 있어야 함"
                )

            return GetCollectingPeriodUtil.get_collecting_period(
                instance=last_region_price
            )

        return GetCollectingPeriodUtil.get_collecting_period(
            start_date=start_date, end_date=end_date
        )

    def _collect_region_price_by_date_and_region(
        self,
        years_and_months,
        regions,
    ) -> bool:
        """
        real_estate.address에 시~리 있는거 가져오기
        real_estate.deals에서 deal 연월에 해당하는거 가져오기
        개수 세기
        매매 총 거래액, 총 평당가
        전세 총 거래액, 총 평당가
        """
        for year_and_month in years_and_months:
            deal_year, deal_month = TimeUtil.split_year_and_month(
                year_and_month=year_and_month
            )
            for region in regions:
                self._collect_region_price(
                    region=region,
                    deal_year=deal_year,
                    deal_month=deal_month,
                )

    def _collect_region_price(
        self,
        region,
        deal_year,
        deal_month,
    ):
        existing_region_price_dict: dict[str, None] = (
            self._create_existing_region_price_dict()
        )
        if self._skip_already_region_price_existing(
            region=region,
            deal_year=deal_year,
            deal_month=deal_month,
            existing_region_price_dict=existing_region_price_dict,
        ):
            return

        self._calc(deal_month, deal_year, region)

    def _calc(self, deal_month, deal_year, region):
        if EnvUtil.not_test_env():
            threads = self._create_calc_region_price_threads(
                region=region, deal_year=deal_year, deal_month=deal_month
            )
            self._start_threads(threads)
        else:
            for deal_type in self.deal_types:
                dto: CollectRegionPriceDto = CollectRegionPriceDto(
                    region=region,
                    deal_type=deal_type,
                    deal_year=deal_year,
                    deal_month=deal_month,
                    is_deal_canceled=False,
                )

                CalcRegionPriceService().calc_region_price(dto=dto)

    def _create_existing_region_price_dict(self) -> dict[str, None]:
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
            deal_date = TimeUtil.get_year_month_day(region_price.deal_date)
            deal_year, deal_month = TimeUtil.split_year_and_month(
                year_and_month=deal_date
            )

            region_price_key = self._create_region_price_key(
                region_id=region_price.region_id,
                deal_year=deal_year,
                deal_month=deal_month,
            )

            region_prices_dict[region_price_key] = None
        return region_prices_dict

    def _skip_already_region_price_existing(
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

    def _create_calc_region_price_threads(
        self, region: Region, deal_year: str, deal_month: str
    ):
        threads = []
        for deal_type in self.deal_types:
            dto: CollectRegionPriceDto = CollectRegionPriceDto(
                region=region,
                deal_type=deal_type,
                deal_year=deal_year,
                deal_month=deal_month,
                is_deal_canceled=False,
            )

            t = threading.Thread(
                target=CalcRegionPriceService().calc_region_price, args=(dto,)
            )
            t.start()
            threads.append(t)
        return threads

    def _start_threads(self, threads):
        if EnvUtil.not_test_env():
            for _thread in threads:
                _thread.join()
