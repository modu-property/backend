from dataclasses import dataclass


@dataclass
class GetDealPriceOfRealEstateDto:
    id: int
    type: str
    latitude: float
    longitude: float
    zoom_level: int
    keyword: str
