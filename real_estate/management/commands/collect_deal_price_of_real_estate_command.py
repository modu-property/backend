from datetime import datetime
import threading
import time
from typing import List
from django.core.management.base import BaseCommand
from modu_property.utils.loggers import logger
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.models import Region
from django.db.models import Count

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

    def get_property_types(self):
        return ["연립다세대"]
        # return ["아파트", "오피스텔", "단독다가구", "연립다세대", "토지", "분양입주권", "공장창고"]

    def get_trade_types(self):
        # return ["매매", "전월세"]
        return ["매매"]

    def get_years_and_months(
        self, start_year: int, start_month: int, end_year: int, end_month: int
    ) -> List[str]:
        from dateutil.relativedelta import relativedelta

        years = end_year - start_year
        months = end_month - start_month

        total_months = years * 12 + months

        years_and_months = [
            datetime.strftime(
                datetime.strptime(f"{start_year}{start_month}", "%Y%m")
                + relativedelta(months=month),
                "%Y%m",
            )
            for month in range(total_months + 1)
        ]
        return years_and_months

    def handle(self, *args, **options):
        sido = options.get("sido")
        regions = []
        qs = Region.objects.values("sido", "regional_code").annotate(c=Count("id"))
        if sido:
            regions = qs.filter(sido=sido)
        else:
            regions = qs.filter(sido__gt="", sigungu="").exclude(sido__contains="출장소")

        regional_codes = []
        for region in regions:
            regional_codes.append(region.get("regional_code"))

        property_types = self.get_property_types()
        trade_types = self.get_trade_types()

        start_year = 2023
        start_month = 1
        end_year = 2023
        end_month = 6

        years_and_months = self.get_years_and_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        for year_and_month in years_and_months:
            start = time.time()
            threads = []
            dto = None
            for property_type in property_types:
                for trade_type in trade_types:
                    for regional_code in regional_codes:
                        dto: CollectDealPriceOfRealEstateDto = (
                            CollectDealPriceOfRealEstateDto(
                                property_type=property_type,
                                year_month=year_and_month,
                                trade_type=trade_type,
                                regional_code=regional_code,
                            )
                        )
                        t = threading.Thread(target=self.service.execute, args=(dto,))
                        t.start()
                        threads.append(t)

            for _thread in threads:
                _thread.join()

            end = time.time()
            logger.info(
                f"부동산 타입 {dto.property_type}, 연월 {dto.year_month}, 매매타입 {dto.trade_type}, 지역코드 {dto.regional_code} 수행시간: %f 초"
                % (end - start)
            )
