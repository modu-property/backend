from typing import Any, Optional, Union
from real_estate.dto.real_estate_dto import GetRealEstatesOnMapDto
from real_estate.models import Deal, RealEstate
from modu_property.utils.loggers import logger
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F
from django.contrib.gis.geos import Point
from django.db.models import QuerySet
from django.db.models import Prefetch, OuterRef, Subquery


class RealEstateRepository:
    def get_real_estate(self, id: int) -> Optional[RealEstate]:
        try:
            return (
                RealEstate.objects.filter(id=id).all().prefetch_related("deals").get()
            )
        except Exception as e:
            logger.error(f"get_real_estate e : {e}")
            return None

    def get_real_estates(self):
        return RealEstate.objects.prefetch_related("deals").all()

    def get_real_estates_by_latitude_and_longitude(
        self, distance_tolerance: int, center_point: Point
    ) -> Union[QuerySet, bool]:
        try:
            subquery = Subquery(
                Deal.objects.filter(real_estate_id=OuterRef("real_estate_id"))
                .order_by("-deal_year", "-deal_month", "-deal_day")
                .values_list("id", flat=True)[:1]
            )
            real_estates: QuerySet = (
                RealEstate.objects.prefetch_related(
                    Prefetch("deals", Deal.objects.filter(id=subquery))
                )
                .annotate(
                    distance=Distance("point", center_point),
                    area_for_exclusive_use_pyung=F(
                        "deals__area_for_exclusive_use_pyung"
                    ),
                    area_for_exclusive_use_price_per_pyung=F(
                        "deals__area_for_exclusive_use_price_per_pyung"
                    ),
                )
                .filter(distance__lte=distance_tolerance, deals__is_deal_canceled=False)
            )
            return real_estates
        except Exception as e:
            logger.error(f"get_real_estates_by_latitude_and_longitude e : {e}")
            return False
