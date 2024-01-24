from typing import Union
from real_estate.models import RealEstate
from modu_property.utils.loggers import logger


class RealEstateRepository:
    def get_real_estate(self, id: int) -> Union[RealEstate, bool]:
        try:
            return (
                RealEstate.objects.filter(id=id).all().prefetch_related("deals").get()
            )
        except Exception as e:
            logger.error(f"get_real_estate e : {e}")
            return False
