import os
import threading
import time
from django.core.management.base import BaseCommand
from manticore.manticore_client import ManticoreClient
from modu_property.utils.loggers import logger
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.property_type_enum import PropertyType
from real_estate.enum.trade_type_enum import TradeType
from real_estate.models import Region
from django.db.models import Count
from modu_property.utils.time import TimeUtil
from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)


class Command(BaseCommand):
    help = "매매, 전월세 내역 수집하는 명령어"

    def __init__(self):
        self.service = CollectDealPriceOfRealEstateService()

    def add_arguments(self, parser):
        parser.add_argument(
            "sido",
            type=str,
            help="서울특별시, 세종특별자치시, ...",
        )

    def handle(self, *args, **options):
        total_period = 0
        sido = options.get("sido")
        regions = []
        qs = Region.objects.values("sido", "regional_code").annotate(c=Count("id"))

        sejong_regional_code = "36110"

        if sido:
            qs = qs.filter(sido=sido)
            regions = qs.exclude(sido__contains="출장소").exclude(sigungu="")

            regional_codes = list(
                set([region.get("regional_code") for region in regions])
            )
        else:
            regional_codes.append(sejong_regional_code)

        property_types = PropertyType.get_property_types()
        trade_types = TradeType.get_trade_types()

        # 2006년부터 수집
        start_year = 2016
        start_month = 1
        end_year = 2016
        end_month = 1

        years_and_months = TimeUtil.get_years_and_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        for year_and_month in years_and_months:
            for property_type in property_types:
                for trade_type in trade_types:
                    start = time.time()
                    threads = []
                    dto = None
                    for regional_code in regional_codes:
                        dto: CollectDealPriceOfRealEstateDto = (
                            CollectDealPriceOfRealEstateDto(
                                property_type=property_type,
                                year_month=year_and_month,
                                trade_type=trade_type,
                                regional_code=regional_code,
                            )
                        )
                        if os.getenv("SERVER_ENV") != "test":
                            t = threading.Thread(
                                target=self.service.execute, args=(dto,)
                            )
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
                        f"부동산 타입 {dto.property_type}, 연월 {dto.year_month}, 매매타입 {dto.trade_type}, 지역코드 {dto.regional_code} 수행시간: %f 초"
                        % (period)
                    )

                    start = time.time()
                    manticore_client = ManticoreClient()
                    manticore_client.run_indexer()
                    end = time.time()
                    period = end - start
                    total_period += period
                    logger.info(f"run manticore indexer 수행시간: %f 초" % (period))

        logger.info(f"total_period : %f초" % (total_period))
