from dataclasses import dataclass


@dataclass
class CollectDealPriceOfRealEstateDto:
    property_type: str
    trade_type: str
    regional_code: str
    year_month: str
