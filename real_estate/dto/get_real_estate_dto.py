from dataclasses import dataclass


@dataclass
class GetRealEstatesOnSearchDto:
    deal_type: str
    keyword: str
    limit: int = None
    real_estate_search_limit: int = None


@dataclass
class GetRealEstatesOnMapDto:
    deal_type: str
    sw_lat: float
    sw_lng: float
    ne_lat: float
    ne_lng: float
    zoom_level: int
    start_year: int
    start_month: int
    end_year: int
    end_month: int


@dataclass
class GetDealsDto:
    real_estate_id: int
    deal_type: str
    page: int
