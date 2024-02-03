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
    latitude: float
    longitude: float
    zoom_level: int
