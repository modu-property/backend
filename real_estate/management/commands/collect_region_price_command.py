from datetime import datetime
import os
import threading
import time
from django.core.management.base import BaseCommand
from modu_property.utils.loggers import logger
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.enum.deal_enum import DealTypesForDBEnum
from modu_property.utils.time import TimeUtil
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_region_price_service import CollectRegionPriceService


class Command(BaseCommand):
    help = "지역 매매, 전세 가격 정보 수집하는 명령어"

    def __init__(self):
        self.service = CollectRegionPriceService()

    def add_arguments(self, parser):
        parser.add_argument(
            "sido",
            type=str,
            help="서울특별시, 세종특별자치시, ...",
        )

    def handle(self, *args, **options):
        total_period = 0
        repository = RealEstateRepository()

        sido = options["sido"]

        regions = repository.get_regions(sido=sido)

        deal_types = [DealTypesForDBEnum.DEAL.value]

        # 2006년부터 수집
        start_year = 2006
        start_month = 1
        end_year = 2006
        end_month = 2

        years_and_months = TimeUtil.get_years_and_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        """
        region_price에 deal_date, region_id가 있으면 제외
        key -> region_id-year-month
        """
        region_prices_dict = {}
        region_prices = list(repository.get_region_prices())
        for region_price in region_prices:
            deal_date = datetime.strftime(region_price.deal_date, "%Y%m%d")
            deal_year = deal_date[:4]
            deal_month = deal_date[4:6]
            region_prices_dict[
                f"{region_price.region_id}-{deal_year}-{deal_month}"
            ] = None

        for year_and_month in years_and_months:
            for region in regions:
                deal_year = year_and_month[:4]
                deal_month = year_and_month[4:]
                key = f"{region.id}-{deal_year}-{deal_month}"

                if key in region_prices_dict:
                    logger.debug(f"{key} 생략")
                    continue

                _region = repository.get_region(
                    sido=region.sido,
                    sigungu=region.sigungu,
                    ubmyundong=region.ubmyundong,
                    dongri=region.dongri,
                )
                start = time.time()
                threads = []
                dto = None
                for deal_type in deal_types:
                    dto: CollectRegionPriceDto = CollectRegionPriceDto(
                        region=_region,
                        deal_type=deal_type,
                        deal_year=deal_year,
                        deal_month=deal_month,
                    )
                    if os.getenv("SERVER_ENV") != "test":
                        t = threading.Thread(target=self.service.execute, args=(dto,))
                        t.start()
                        threads.append(t)
                    else:
                        self.service.execute(dto=dto)

                if os.getenv("SERVER_ENV") != "test":
                    for _thread in threads:
                        _thread.join()

                end = time.time()
                period = end - start
                total_period += period
                logger.info(
                    f"region {dto.region}, deal_type {dto.deal_type}, deal_year {dto.deal_year}, deal_month {dto.deal_month} 수행시간: %f 초"
                    % (period)
                )

        logger.info(f"total_period : %f초" % (total_period))
