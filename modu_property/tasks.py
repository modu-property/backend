import threading
import time
from celery import shared_task
from modu_property.utils.loggers import logger
from modu_property.utils.time import TimeUtil
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.property_type_enum import PropertyType
from real_estate.enum.trade_type_enum import TradeType
from real_estate.models import Region
from django.db.models import Count

from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)

# TODO : 1시간마다 현재연월/전체법정동코드 싹 수집


@shared_task
def collect_deal_price_of_real_estate_task(
    sido: str,
):
    regions = []
    qs = Region.objects.values("sido", "regional_code").annotate(c=Count("id"))
    sejong_regional_code = "36110"
    qs = qs.filter(sido=sido)
    regions = qs.exclude(sido__contains="출장소").exclude(sigungu="")

    regional_codes = list(set([region.get("regional_code") for region in regions]))
    regional_codes.append(sejong_regional_code)

    service = CollectDealPriceOfRealEstateService()

    property_types = PropertyType.get_property_types()
    trade_types = TradeType.get_trade_types()

    year_and_month = TimeUtil.get_current_year_and_month()

    for property_type in property_types:
        for trade_type in trade_types:
            start = time.time()
            threads = []
            dto = None
            for regional_code in regional_codes:
                dto: CollectDealPriceOfRealEstateDto = CollectDealPriceOfRealEstateDto(
                    property_type=property_type,
                    year_month=year_and_month,
                    trade_type=trade_type,
                    regional_code=regional_code,
                )
                t = threading.Thread(target=service.execute, args=(dto,))
                t.start()
                threads.append(t)

            for _thread in threads:
                _thread.join()

            end = time.time()
            logger.info(
                f"부동산 타입 {dto.property_type}, 연월 {dto.year_month}, 매매타입 {dto.trade_type}, 지역코드 {dto.regional_code} 수행시간: %f 초"
                % (end - start)
            )
