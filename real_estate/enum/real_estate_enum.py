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
    MULTI_UNIT_HOUSE = "MULTI_UNIT_HOUSE"  # 연립/다세대
    APARTMENT = "APARTMENT"
    OFFICETEL = "OFFICETEL"
    MULTI_HOUSEHOLD = "MULTI_HOUSEHOLD"  # 다가구
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
    # dongri 단위는 없는 지역이 많아서 보여주지 않기로 함.
    UBMYUNDONG = 6
    SIGUNGU = 7
    SIDO = 8


class RegionCodeEnum(Enum):
    SEJONG = "36110"


class SearchLimitEnum(Enum):
    REGION = 3
    REAL_ESTATES = 15


class RealEstateKeyEnum(Enum):
    건축년도 = "buildYear"
    매수자 = "buyerGbn"
    해제사유발생일 = "cdealDay"
    해제여부 = "cdealType"
    거래금액 = "dealAmount"
    계약일 = "dealDay"
    계약월 = "dealMonth"
    계약년도 = "dealYear"
    거래유형 = "dealingGbn"
    중개사소재지 = "estateAgentSggNm"
    전용면적 = "excluUseAr"
    층 = "floor"
    지번 = "jibun"
    대지권면적 = "landAr"
    연립다세대명 = "mhouseNm"
    등기일자 = "rgstData"
    지역코드 = "sggCd"
    매도자 = "slerGbn"
    법정동 = "umdNm"
