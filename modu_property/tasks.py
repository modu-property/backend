from celery import shared_task
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto

from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)

# TODO : 주기적으로 수집, multiprocessing?, 특정 날짜부터 쭉 수집하다가 현재 연월과 같아지면 현재 연월만 수집?

"""
특정 날짜부터 쭉 수집
"""

# @shared_task
# def collect_property_news_task(display: int):
#     property_types= ["연립다세대"]
#     trade_types = ["매매"]
#     regional_codes = [""]


#     dto: CollectDealPriceOfRealEstateDto(
#         property_type="연립다세대",
#         trade_type="매매",
#         regional_code="11110",
#         year_month="202001",
#     )
#     service = CollectDealPriceOfRealEstateService().execute()
#     service.execute()
