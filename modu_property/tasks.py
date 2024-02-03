import threading
import time
from celery import shared_task
from modu_property.utils.loggers import logger
from modu_property.utils.time import TimeUtil
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.real_estate_enum import RealEstateTypesForQueryEnum
from real_estate.enum.deal_enum import DealTypesForQueryEnum
from real_estate.models import Region
from django.db.models import Count

from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)
from manticore.manticore_client import ManticoreClient


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

    real_estate_types = RealEstateTypesForQueryEnum.get_real_estate_types()
    deal_types = DealTypesForQueryEnum.get_deal_types()

    year_and_month = TimeUtil.get_current_year_and_month()

    for real_estate_type in real_estate_types:
        for deal_type in deal_types:
            start = time.time()
            threads = []
            dto = None
            for regional_code in regional_codes:
                dto: CollectDealPriceOfRealEstateDto = CollectDealPriceOfRealEstateDto(
                    real_estate_type=real_estate_type,
                    year_month=year_and_month,
                    deal_type=deal_type,
                    regional_code=regional_code,
                )
                t = threading.Thread(target=service.execute, args=(dto,))

                t.start()
                threads.append(t)

            for _thread in threads:
                _thread.join()

            end = time.time()
            logger.info(
                f"부동산 타입 {dto.real_estate_type}, 연월 {dto.year_month}, 매매타입 {dto.deal_type}, 지역코드 {dto.regional_code} 수행시간: %f 초"
                % (end - start)
            )

    start = time.time()
    manticore_client = ManticoreClient()
    manticore_client.run_indexer()
    end = time.time()
    logger.info(f"run manticore indexer 수행시간: %f 초" % (end - start))
