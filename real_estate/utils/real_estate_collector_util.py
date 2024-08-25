from time import sleep

from typing import Union
from PublicDataReader import TransactionPrice
from dependency_injector.wiring import Provide
from pandas import DataFrame
from modu_property.utils.loggers import logger
from real_estate.containers.utils.third_party_container import (
    ThirdPartyContainer,
)

from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto


class RealEstateCollectorUtil:
    def __init__(
        self,
        transaction_price: TransactionPrice = Provide[
            ThirdPartyContainer.transaction_price
        ],
    ) -> None:
        self.transaction_price = transaction_price

    def collect_deal_price_of_real_estate(
        self, dto: CollectDealPriceOfRealEstateDto
    ) -> Union[DataFrame, bool]:
        try:
            sleep(0.0005)
            return self.get_data(dto)
        except Exception as e:
            logger.error(
                e,
                f"get_deal_price_of_real_estate 수집 실패 dto : {dto.__dict__}",
            )
            return False

    def get_data(self, dto):
        return self.transaction_price.get_data(
            property_type=dto.real_estate_type,
            trade_type=dto.deal_type,
            sigungu_code=dto.regional_code,
            year_month=dto.year_month,
        )
