from enum import Enum


class PropertyType(Enum):
    MULTI_UNIT_HOUSE = "연립다세대"
    # APARTMENT = "아파트"
    # OFFICETEL = "오피스텔"
    # MULTI_HOUSEHOLD = "단독다가구"
    # LAND = "토지"
    # OWNERSHIP = "분양입주권"
    # FACTORY_WAREHOUSE = "공장창고"

    @classmethod
    def get_property_types(self):
        return [e.value for e in PropertyType]
