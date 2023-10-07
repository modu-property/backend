from dataclasses import dataclass

@dataclass
class GetDealPriceOfVillaDto:
    type: str
    latitude: str
    longitude: str
    zoom_level: int
    keyword: str
