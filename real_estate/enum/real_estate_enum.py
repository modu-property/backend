from enum import Enum


class RealEstateTypesForQueryEnum(Enum):
    MULTI_UNIT_HOUSE = "연립다세대"
    # APARTMENT = "아파트"
    # OFFICETEL = "오피스텔"
    # MULTI_HOUSEHOLD = "단독다가구"
    # LAND = "토지"
    # OWNERSHIP = "분양입주권"
    # FACTORY_WAREHOUSE = "공장창고"

    @classmethod
    def get_real_estate_types(cls):
        return [e.value for e in RealEstateTypesForQueryEnum]


class RealEstateTypesForDBEnum(Enum):
    MULTI_UNIT_HOUSE = "MULTI_UNIT_HOUSE"
    APARTMENT = "APARTMENT"
    OFFICETEL = "OFFICETEL"
    MULTI_HOUSEHOLD = "MULTI_HOUSEHOLD"
    LAND = "LAND"
    OWNERSHIP = "OWNERSHIP"
    FACTORY_WAREHOUSE = "FACTORY_WAREHOUSE"


REAL_ESTATE_TYPES = (
    (
        RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.name,
        RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value,
    ),
)


class RealEstateZoomLevelEnum(Enum):
    DEFAULT = 4
    MIN = 1
    MAX = 5


class RegionZoomLevelEnum(Enum):
    DONGRI = 6
    UBMYUNDONG = 7
    SIGUNGU = 8
    SIDO = 9


class RegionCodeEnum(Enum):
    SEJONG = "36110"


class SearchLimitEnum(Enum):
    REGION = 3
    REAL_ESTATES = 15
