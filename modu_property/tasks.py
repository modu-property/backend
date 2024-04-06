import threading
import requests
from celery import shared_task
from modu_property.utils.time import TimeUtil
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.real_estate_enum import RealEstateTypesForQueryEnum
from real_estate.enum.deal_enum import DealTypesForQueryEnum
from real_estate.repository.real_estate_repository import RealEstateRepository

from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)
from modu_property.utils.loggers import logger


# TODO : 1시간마다 현재연월/전체법정동코드 싹 수집


@shared_task
def collect_deal_price_of_real_estate_task(
    sido: str,
):
    repository = RealEstateRepository()
    sejong_regional_code = "36110"

    regions = []
    # qs = Region.objects.values("sido", "regional_code").annotate(c=Count("id"))
    # qs = qs.filter(sido=sido)
    # regions = qs.exclude(sido__contains="출장소").exclude(sigungu="")

    regions = repository.get_regions_exclude_branch(sido=sido)

    regional_codes = list(set([region.get("regional_code") for region in regions]))
    regional_codes.append(sejong_regional_code)

    year_and_month = TimeUtil.get_current_year_and_month()
    run_service(regional_codes=regional_codes, year_and_month=year_and_month)


def run_service(regional_codes, year_and_month):
    try:
        service = CollectDealPriceOfRealEstateService()

        real_estate_types = RealEstateTypesForQueryEnum.get_real_estate_types()
        deal_types = DealTypesForQueryEnum.get_deal_types()

        for real_estate_type in real_estate_types:
            for deal_type in deal_types:
                threads = []
                dto = None
                for regional_code in regional_codes:
                    dto: CollectDealPriceOfRealEstateDto = (
                        CollectDealPriceOfRealEstateDto(
                            real_estate_type=real_estate_type,
                            year_month=year_and_month,
                            deal_type=deal_type,
                            regional_code=regional_code,
                        )
                    )
                    t = threading.Thread(
                        target=service.collect_deal_price_of_real_estate, args=(dto,)
                    )

                    t.start()
                    threads.append(t)

                for _thread in threads:
                    _thread.join()

        requests.get("http://host.docker.internal:8000/manticore")
    except Exception as e:
        logger.error(e)
