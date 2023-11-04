from dataclasses import dataclass


@dataclass
class GetDealPriceOfVillaDto:
    id: int
    type: str
    latitude: float
    longitude: float
    zoom_level: int
    keyword: str
