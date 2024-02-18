from datetime import datetime
from typing import List
from dateutil.relativedelta import relativedelta


class TimeUtil:
    @classmethod
    def get_years_and_months(
        self,
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

    @classmethod
    def get_current_year_and_month(self):
        _now = datetime.now()
        year = _now.year
        month = _now.month

        return datetime.strftime(datetime.strptime(f"{year}{month}", "%Y%m"), "%Y%m")
