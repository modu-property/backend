import os
import PublicDataReader as pdr

from PublicDataReader import TransactionPrice
from pandas import DataFrame

from modu_property.utils.loggers import logger
from real_estate.models import Region


class AddressCollector:
    def __init__(self) -> None:
        self.service_key = os.getenv("SERVICE_KEY")
        self.api = TransactionPrice(self.service_key)

    def collect_regional_info(self) -> bool:
        """
        법정동 코드, 시도, 시군구, 읍면동 수집
        """
        table: DataFrame = pdr.code_bdong()

        region_models = []
        for _, row in table.iterrows():
            if not row.get("말소일자"):
                sido = row.get("시도명", None)
                regional_code = row.get("시군구코드", None)
                sigungu = row.get("시군구명", None)
                ubmyundong = row.get("읍면동명", None)
                dongri = row.get("동리명", None)
                region_models.append(
                    Region(
                        sido=sido,
                        regional_code=regional_code,
                        sigungu=sigungu,
                        ubmyundong=ubmyundong,
                        dongri=dongri,
                    )
                )

        try:
            Region.objects.bulk_create(region_models)
            return True
        except Exception as e:
            logger.error(f"collect_regional_info bulk_create 실패 e : {e}")
            return False
