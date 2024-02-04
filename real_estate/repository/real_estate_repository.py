from typing import Any, List, Optional, Union
from real_estate.dto.real_estate_dto import GetRealEstatesOnMapDto
from real_estate.models import Deal, RealEstate, Region
from modu_property.utils.loggers import logger
from django.db.models import (
    F,
    QuerySet,
    Prefetch,
    OuterRef,
    Subquery,
    Value,
    DateField,
)
from django.db.models.functions import Concat


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

    def get_real_estates_in_rectangle(self, dto: GetRealEstatesOnMapDto):
        """
        시, 군, 구, 동이 아닌 개별 부동산 정보를 응답함
        """
        try:
            subquery = Subquery(
                Deal.objects.filter(real_estate_id=OuterRef("real_estate_id"))
                .order_by("-deal_year", "-deal_month", "-deal_day")
                .values_list("id", flat=True)[:1]
            )
            real_estates: QuerySet = (
                RealEstate.objects.annotate(
                    deal_date=Concat(
                        "deals__deal_year",
                        Value("-"),
                        "deals__deal_month",
                        Value("-"),
                        "deals__deal_day",
                        output_field=DateField(),
                    ),
                    area_for_exclusive_use_pyung=F(
                        "deals__area_for_exclusive_use_pyung"
                    ),
                    area_for_exclusive_use_price_per_pyung=F(
                        "deals__area_for_exclusive_use_price_per_pyung"
                    ),
                    deal_price=F("deals__deal_price"),
                )
                .prefetch_related(Prefetch("deals", Deal.objects.filter(id=subquery)))
                .filter(
                    deals__is_deal_canceled=False,
                    latitude__gte=dto.sw_lat,
                    latitude__lte=dto.ne_lat,
                    longitude__gte=dto.sw_lng,
                    longitude__lte=dto.ne_lng,
                )
            )
            return real_estates
        except Exception as e:
            logger.error(f"get_real_estates_in_rectangle e : {e}")
            return False

    def bulk_create_regions(
        self, region_models: List[Region]
    ) -> Union[List[Region], bool]:
        try:
            result: list[Region] = Region.objects.bulk_create(region_models)
            return result
        except Exception as e:
            logger.error(f"bulk_create_regions 실패 e : {e}")
            return False

    def update_region(self, region: Region) -> bool:
        try:
            region.save()
            return True
        except Exception as e:
            logger.error(f"update_region 실패 e : {e}")
            return False

    def get_regions(self) -> Union[QuerySet, bool]:
        try:
            return Region.objects.all()
        except Exception as e:
            logger.error(f"get_regions 실패 e : {e}")
            return False
