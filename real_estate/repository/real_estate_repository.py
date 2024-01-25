from typing import Any, Union
from real_estate.dto.real_estate_dto import GetRealEstatesOnMapDto
from real_estate.models import RealEstate
from modu_property.utils.loggers import logger
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F
from django.contrib.gis.geos import Point
from django.db.models import QuerySet


class RealEstateRepository:
    def get_real_estate(self, id: int) -> Union[RealEstate, bool]:
        try:
            return (
                RealEstate.objects.filter(id=id).all().prefetch_related("deals").get()
            )
        except Exception as e:
            logger.error(f"get_real_estate e : {e}")
            return False

    def get_real_estates(self):
        return RealEstate.objects.all()

    def get_real_estates_by_latitude_and_longitude(
        self, distance_tolerance: int, center_point: Point
    ) -> Union[list[dict], bool]:
        try:
            real_estates: list[dict] = list(
                RealEstate.objects.prefetch_related("deals")
                .annotate(
                    distance=Distance("point", center_point),
                    area_for_exclusive_use_pyung=F(
                        "deals__area_for_exclusive_use_pyung"
                    ),
                    area_for_exclusive_use_price_per_pyung=F(
                        "deals__area_for_exclusive_use_price_per_pyung"
                    ),
                )
                .filter(distance__lte=distance_tolerance)
                .values(
                    "id",
                    "latitude",
                    "longitude",
                    "area_for_exclusive_use_pyung",
                    "area_for_exclusive_use_price_per_pyung",
                )
            )
            return real_estates
        except Exception as e:
            logger.error(f"get_real_estates_by_latitude_and_longitude e : {e}")
            return False
