from dataclasses import dataclass
from decimal import Decimal

from real_estate.models import Region


@dataclass
class CollectRegionPriceDto:
    region: Region = None
    deal_year: int = None
    deal_month: int = None
    deal_type: str = None
    is_deal_canceled: bool = None

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
