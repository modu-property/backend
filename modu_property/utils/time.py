from datetime import datetime
from functools import wraps
import time
from typing import List
from dateutil.relativedelta import relativedelta
from modu_property.utils.loggers import logger


class TimeUtil:
    @staticmethod
    def get_years_and_months(
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
        format: str = "%Y%m",
    ) -> List[str]:
        years = end_year - start_year
        months = end_month - start_month

        total_months = years * 12 + months

        years_and_months = [
            datetime.strftime(
                datetime.strptime(f"{start_year}{start_month}", format)
                + relativedelta(months=month),
                format,
            )
            for month in range(total_months + 1)
        ]
        return years_and_months

    @staticmethod
    def get_current_year_and_month():
        _now = datetime.now()
        year = _now.year
        month = _now.month

        return datetime.strftime(datetime.strptime(f"{year}{month}", "%Y%m"), "%Y%m")

    @staticmethod
    def split_year_and_month(year_and_month: str) -> tuple[int, int]:
        if "-" in year_and_month:
            year_and_month = year_and_month.split("-")
        return int(year_and_month[:4]), int(year_and_month[4:6])

    @staticmethod
    def timer(func):
        @wraps(func)
        def timer_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time

            logger.debug(
                f"timer [{func.__name__}] {args} {kwargs} Took {total_time:.4f} seconds"
            )
            return result

        return timer_wrapper
