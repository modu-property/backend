from dataclasses import dataclass


@dataclass
class GetRealEstateDto:
    id: int


@dataclass
class GetRealEstatesOnSearchDto:
    type: str
    keyword: str


@dataclass
class GetRealEstatesOnMapDto:
    type: str
    latitude: float
    longitude: float
    zoom_level: int
