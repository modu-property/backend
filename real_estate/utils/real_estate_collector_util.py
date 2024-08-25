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

# TODO : 컬럼, url 신규로 수정해야 함
META_DICT = {
    "아파트": {
        "매매": {
            "url": "",
            "columns": [
                "지역코드",
                "도로명",
                "법정동",
                "지번",
                "아파트",
                "건축년도",
                "층",
                "전용면적",
                "년",
                "월",
                "일",
                "거래금액",
                "도로명건물본번호코드",
                "도로명건물부번호코드",
                "도로명시군구코드",
                "도로명일련번호코드",
                "도로명지상지하코드",
                "도로명코드",
                "법정동본번코드",
                "법정동부번코드",
                "법정동시군구코드",
                "법정동읍면동코드",
                "법정동지번코드",
                "일련번호",
                "거래유형",
                "중개사소재지",
                "해제사유발생일",
                "해제여부",
            ],
        },
        "전월세": {
            "url": "",
            "columns": [
                "지역코드",
                "법정동",
                "지번",
                "아파트",
                "건축년도",
                "층",
                "전용면적",
                "년",
                "월",
                "일",
                "보증금액",
                "월세금액",
                "계약구분",
                "계약기간",
                "갱신요구권사용",
                "종전계약보증금",
                "종전계약월세",
            ],
        },
    },
    "오피스텔": {
        "매매": {
            "url": "",
            "columns": [
                "지역코드",
                "시군구",
                "법정동",
                "지번",
                "단지",
                "건축년도",
                "층",
                "전용면적",
                "년",
                "월",
                "일",
                "거래금액",
                "거래유형",
                "중개사소재지",
                "해제사유발생일",
                "해제여부",
            ],
        },
        "전월세": {
            "url": "",
            "columns": [
                "지역코드",
                "시군구",
                "법정동",
                "지번",
                "단지",
                "건축년도",
                "층",
                "전용면적",
                "년",
                "월",
                "일",
                "보증금",
                "월세",
                "계약구분",
                "계약기간",
                "갱신요구권사용",
                "종전계약보증금",
                "종전계약월세",
            ],
        },
    },
    "연립다세대": {
        "매매": {
            "url": "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade",
            "columns": [
                "buildYear",
                "buyerGbn",
                "cdealDay",
                "cdealType",
                "dealAmount",
                "dealDay",
                "dealMonth",
                "dealYear",
                "dealingGbn",
                "estateAgentSggNm",
                "excluUseAr",
                "floor",
                "jibun",
                "landAr",
                "mhouseNm",
                "rgstData",
                "sggCd",
                "slerGbn",
                "umdNm",
            ],
        },
        "전월세": {
            "url": "",
            "columns": [
                "지역코드",
                "법정동",
                "지번",
                "연립다세대",
                "건축년도",
                "층",
                "전용면적",
                "년",
                "월",
                "일",
                "보증금액",
                "월세금액",
                "계약구분",
                "계약기간",
                "갱신요구권사용",
                "종전계약보증금",
                "종전계약월세",
            ],
        },
    },
}


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
            self._change_to_new_api(dto=dto)
            return self.get_data(dto)
        except Exception as e:
            logger.error(
                e,
                f"get_deal_price_of_real_estate 수집 실패 dto : {dto.__dict__}",
            )
            return False

    def _change_to_new_api(self, dto: CollectDealPriceOfRealEstateDto):
        self.transaction_price.meta_dict[dto.real_estate_type][
            dto.deal_type
        ] = META_DICT[dto.real_estate_type][dto.deal_type]

    def get_data(self, dto):
        return self.transaction_price.get_data(
            property_type=dto.real_estate_type,
            trade_type=dto.deal_type,
            sigungu_code=dto.regional_code,
            year_month=dto.year_month,
        )
