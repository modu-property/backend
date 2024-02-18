from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from real_estate.models import Region


@dataclass
class CollectRegionPriceDto:
    region: Region
    deal_type: str
    deal_year: int
    deal_month: int

    total_deal_price: int = 0
    total_deal_price_per_pyung: Decimal = Decimal()
    total_jeonse_price: int = 0
    total_jeonse_price_per_pyung: Decimal = Decimal()
    average_deal_price: str = ""
    average_jeonse_price: str = ""
    average_deal_price_per_pyung: str = ""
    average_jeonse_price_per_pyung: str = ""
    deal_count: int = 0
    jeonse_count: int = 0
    deal_date: str = None
    target_region: str = ""
