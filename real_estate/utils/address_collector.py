import os
import PublicDataReader as pdr

from PublicDataReader import TransactionPrice
from pandas import DataFrame

from modu_property.utils.logger import logger
from real_estate.models import RegionalCode


# django  command로 db에 한번 싹 넣기
class AddressCollector:
    def __init__(self) -> None:
        self.service_key = os.getenv("SERVICE_KEY")
        self.api = TransactionPrice(self.service_key)

    def collect_regional_info(self) -> bool:
        """
        법정동 코드, 시도, 시군구, 읍면동 수집
        """
        table: DataFrame = pdr.code_bdong()

        regional_codes = []
        regional_code_models = []
        # TODO : 일단 지역 코드만 수집하고 매매/전월세 전체 내역 다 가져오는지 확인
        for index, row in table.iterrows():
            if not row.get("말소일자"):
                regional_code = row.get("시군구코드")
                regional_codes.append(regional_code)

        regional_codes = set(regional_codes)

        for regional_code in regional_codes:
            regional_code_models.append(RegionalCode(regional_code=regional_code))

        try:
            RegionalCode.objects.bulk_create(regional_code_models)
            return True
        except Exception as e:
            logger.info(f"collect_regional_info bulk_create 실패 e : {e}")
            return False
