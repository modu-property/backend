from dataclasses import dataclass


@dataclass
class GetRealEstateDto:
    id: int


@dataclass
class GetRealEstatesOnSearchDto:
    deal_type: str
    keyword: str
    limit: int


@dataclass
class GetRealEstatesOnMapDto:
    deal_type: str
    sw_lat: float
    sw_lng: float
    ne_lat: float
    ne_lng: float
    zoom_level: int
