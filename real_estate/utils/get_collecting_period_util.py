from datetime import datetime, timedelta
from typing import Union, List

from modu_property.utils.time import TimeUtil
from real_estate.models import RegionPrice, Deal


class GetCollectingPeriodUtil:
    @classmethod
    def get_collecting_period(
        cls,
        instance: Union[RegionPrice, Deal, None] = None,
        start_date: str = "",
        end_date: str = "",
    ) -> List[str]:
        start_year, start_month, end_year, end_month = 0, 0, 0, 0
        if instance:
            end_month, end_year, start_month, start_year = (
                cls._get_dates_from_instance(
                    end_month, end_year, instance, start_month, start_year
                )
            )
        else:
            end_month, end_year, start_month, start_year = (
                cls._get_dates_from_dates(
                    end_date,
                    end_month,
                    end_year,
                    start_date,
                    start_month,
                    start_year,
                )
            )

        years_and_months = TimeUtil.get_years_and_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
        )

        return years_and_months

    @classmethod
    def _get_dates_from_dates(
        cls, end_date, end_month, end_year, start_date, start_month, start_year
    ):
        start_year: int = int(start_date[:4])
        start_month: int = int(start_date[4:])
        end_year: int = int(end_date[:4])
        end_month: int = int(end_date[4:])
        return end_month, end_year, start_month, start_year

    @classmethod
    def _get_dates_from_instance(
        cls, end_month, end_year, instance, start_month, start_year
    ):
        start_year, start_month = TimeUtil.split_year_and_month(
            year_and_month=datetime.strftime(instance.deal_date, "%Y%m%d")
        )
        end_date = datetime.strftime(
            instance.deal_date + timedelta(weeks=52 * 2), "%Y%m%d"
        )
        end_year, end_month = TimeUtil.split_year_and_month(
            year_and_month=end_date
        )
        return end_month, end_year, start_month, start_year
