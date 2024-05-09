from dataclasses import dataclass


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


@dataclass
class GetDealsDto:
    real_estate_id: int
    deal_type: str
    page: int
