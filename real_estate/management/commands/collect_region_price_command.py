from datetime import datetime, timedelta
import os
import threading
from django.core.management.base import BaseCommand
from modu_property.utils.loggers import logger
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from modu_property.utils.time import TimeUtil
from real_estate.models import Region
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_region_price_service import CollectRegionPriceService


class Command(BaseCommand):
    help = "지역 매매, 전세 가격 정보 수집하는 명령어"

    def __init__(self):
        self.service = CollectRegionPriceService()
        self.deal_types = [DealTypesForDBEnum.DEAL.value]
        self.repository = RealEstateRepository()
        self.total_period = 0

    @TimeUtil.timer
    def handle(self, *args, **options):
        sido, start_year, start_month, end_year, end_month = self.get_command_params(
            options
        )

        years_and_months = self.get_collect_period(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        regions = self.repository.get_regions(sido=sido)
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

                if self._continue(
                    region=region,
                    deal_year=deal_year,
                    deal_month=deal_month,
                    existing_region_price_dict=existing_region_price_dict,
                ):
                    continue

                _region = self.repository.get_region(
                    sido=region.sido,
                    sigungu=region.sigungu,
                    ubmyundong=region.ubmyundong,
                    dongri=region.dongri,
                )
                if not _region:
                    raise Exception(f"specific region not found : {region.__dict__}")

                self.run_service(
                    deal_year=deal_year, deal_month=deal_month, _region=_region
                )

    def get_collect_period(
        self, start_year: int, start_month: int, end_year: int, end_month: int
    ):
        start_year, start_month, end_year, end_month = self.get_start_date_and_end_date(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        years_and_months = TimeUtil.get_years_and_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        return years_and_months

    def add_arguments(self, parser):
        parser.add_argument(
            "sido",
            type=str,
            help="서울특별시, 세종특별자치시, ...",
        )
        parser.add_argument(
            "start_year",
            type=int,
            help="2006",
        )
        parser.add_argument(
            "start_month",
            type=int,
            help="1",
        )
        parser.add_argument(
            "end_year",
            type=int,
            help="2006",
        )
        parser.add_argument(
            "end_month",
            type=int,
            help="12",
        )

    def get_command_params(self, options):
        sido = options.get("sido")
        start_year = options.get("start_year", 0)
        start_month = options.get("start_month", 0)
        end_year = options.get("end_year", 0)
        end_month = options.get("end_month", 0)
        return sido, start_year, start_month, end_year, end_month

    def get_start_date_and_end_date(
        self, start_year: int, start_month: int, end_year: int, end_month: int
    ):
        if not all([start_year, start_month, end_year, end_month]):
            region_price = self.repository.get_last_region_price()
            if not region_price:
                raise Exception(
                    "시작/종료 연월과 region_price 둘 다 없음. 둘 중에 하나는 있어야 함"
                )

            end_date = datetime.strftime(
                region_price.deal_date + timedelta(weeks=52 * 2), "%Y%m%d"
            )

            start_year, start_month = TimeUtil.split_year_and_month(
                year_and_month=datetime.strftime(region_price.deal_date, "%Y%m%d")
            )
            end_year, end_month = TimeUtil.split_year_and_month(year_and_month=end_date)
        return start_year, start_month, end_year, end_month

    def create_existing_region_price_dict(self) -> dict[str, None]:
        """
        region_price에 deal_date, region_id가 있으면 제외
        key -> region-id-year-month
        """
        region_prices_dict = {}
        region_prices = self.repository.get_region_prices()
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

    def run_service(self, deal_year: int, deal_month: int, _region: Region) -> None:
        dto = None
        threads = []
        for deal_type in self.deal_types:
            dto: CollectRegionPriceDto = CollectRegionPriceDto(
                region=_region,
                deal_type=deal_type,
                deal_year=deal_year,
                deal_month=deal_month,
                is_deal_canceled=False,
            )
            if self.not_test_env():
                t = threading.Thread(target=self.service.execute, args=(dto,))
                t.start()
                threads.append(t)
            else:
                self.service.execute(dto=dto)

        if self.not_test_env():
            for _thread in threads:
                _thread.join()

    def not_test_env(self) -> bool:
        return os.getenv("SERVER_ENV") != "test"

    def create_region_price_key(
        self, region_id: int, deal_year: str, deal_month: str
    ) -> str:
        return f"{region_id}-{deal_year}-{deal_month}"

    def _continue(self, region, deal_year, deal_month, existing_region_price_dict):
        region_price_key = self.create_region_price_key(
            region_id=region.id, deal_year=deal_year, deal_month=deal_month
        )

        if region_price_key in existing_region_price_dict:
            return True
