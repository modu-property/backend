import logging
import os

from typing import Union
from PublicDataReader import TransactionPrice
from pandas import DataFrame

from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto

logger = logging.getLogger("django")


class RealEstateCollector:
    def __init__(self) -> None:
        self.service_key = os.getenv("SERVICE_KEY")
        self.api = TransactionPrice(self.service_key)

    def collect_deal_price_of_real_estate(
        self, dto: CollectDealPriceOfRealEstateDto
    ) -> Union[DataFrame, bool]:
        try:
            return self.api.get_data(
                property_type=dto.property_type,
                trade_type=dto.trade_type,
                sigungu_code=dto.regional_code,
                year_month=dto.year_month,
            )
        except Exception as e:
            logger.error(e, "get_deal_price_of_real_estate 수집 실패")
            return False
