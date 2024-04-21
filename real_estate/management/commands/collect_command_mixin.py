import os

from datetime import datetime, timedelta
from typing import Union
from modu_property.utils.time import TimeUtil
from real_estate.models import Deal, RegionPrice
from real_estate.repository.real_estate_repository import RealEstateRepository


class CollectCommandMixin:
    def __init__(self) -> None:
        self.real_estate_repository = RealEstateRepository()

    @staticmethod
    def get_collecting_period(
        instance: Union[RegionPrice, Deal, None] = None,
        start_date: str = "",
        end_date: str = "",
    ):
        start_year, start_month, end_year, end_month = 0, 0, 0, 0
        if instance:
            start_year, start_month = TimeUtil.split_year_and_month(
                year_and_month=datetime.strftime(instance.deal_date, "%Y%m%d")
            )
            end_date = datetime.strftime(
                instance.deal_date + timedelta(weeks=52 * 2), "%Y%m%d"
            )
            end_year, end_month = TimeUtil.split_year_and_month(
                year_and_month=end_date
            )
        else:
            start_year: int = int(start_date[:4])
            start_month: int = int(start_date[4:])
            end_year: int = int(end_date[:4])
            end_month: int = int(end_date[4:])

        years_and_months = TimeUtil.get_years_and_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        return years_and_months

    @staticmethod
    def get_command_params(options):
        sido = options.get("sido")
        start_date = options.get("start_date", 0)
        end_date = options.get("end_date", 0)
        return sido, start_date, end_date

    @staticmethod
    def not_test_env() -> bool:
        return os.getenv("SERVER_ENV") != "test"
