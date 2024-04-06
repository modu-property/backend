from dataclasses import dataclass


@dataclass
class CollectDealPriceOfRealEstateDto:
    real_estate_type: str
    deal_type: str
    regional_code: str
    year_month: str
