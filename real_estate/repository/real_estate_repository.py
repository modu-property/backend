from typing import List, Optional, Union
from django.forms import model_to_dict
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.dto.get_real_estate_dto import GetDealsDto, GetRealEstatesOnMapDto
from real_estate.enum.real_estate_enum import RegionZoomLevelEnum
from real_estate.models import Deal, RealEstate, Region, RegionPrice
from modu_property.utils.loggers import logger
from django.db.models import (
    F,
    QuerySet,
    Prefetch,
    OuterRef,
    Subquery,
    Value,
    DateField,
    Count,
)
from django.db.models.functions import Concat
from real_estate.serializers import RegionPriceSerializer


class RealEstateRepository:
    def get_real_estate(self, id: int) -> Optional[RealEstate]:
        try:
            return RealEstate.objects.filter(id=id).get()
        except Exception as e:
            logger.error(f"get_real_estate e : {e}")
            return None

    def get_real_estates(self, dto: CollectRegionPriceDto = None):
        _qs = RealEstate.objects

        if isinstance(dto, CollectRegionPriceDto) and dto.target_region:
            return (
                _qs.filter(address__contains=dto.target_region)
                .prefetch_related(
                    Prefetch(
                        "deals",
                        Deal.objects.filter(
                            deal_year=dto.deal_year,
                            deal_month=dto.deal_month,
                            deal_type=dto.deal_type,
                            is_deal_canceled=dto.is_deal_canceled,
                        ),
                    )
                )
                .all()
            )

        return _qs.prefetch_related("deals").all()

    def get_individual_real_estates(self, dto: GetRealEstatesOnMapDto):
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
            return real_estates[:150]
        except Exception as e:
            logger.error(f"get_individual_real_estates e : {e}")
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

    def get_regions(self, sido: str = "") -> Union[QuerySet, bool]:
        _q = Region.objects
        if sido:
            return _q.filter(sido=sido)
        else:
            return _q.all()

    def get_regions_exclude_branch(self, sido: str):
        qs = Region.objects.values("sido", "regional_code").annotate(c=Count("id"))
        qs = qs.filter(sido=sido)
        regions = qs.exclude(sido__contains="출장소").exclude(sigungu="")
        return regions

    def get_region(
        self, sido: str = "", sigungu: str = "", ubmyundong: str = "", dongri: str = ""
    ):
        _q = Region.objects

        if dongri:
            _q = _q.filter(
                sido=sido, sigungu=sigungu, ubmyundong=ubmyundong, dongri=dongri
            )
        elif ubmyundong:
            _q = _q.filter(sido=sido, sigungu=sigungu, ubmyundong=ubmyundong, dongri="")
        elif sigungu:
            _q = _q.filter(sido=sido, sigungu=sigungu, ubmyundong="", dongri="")
        elif sido:
            _q = _q.filter(sido=sido, sigungu="", ubmyundong="", dongri="")

        try:
            return _q.get()
        except Exception as e:
            logger.error(f"get_region 실패 e : {e}")
            return False

    def create_region_price(
        self, dto: CollectRegionPriceDto
    ) -> Union[RegionPrice, bool]:
        try:
            model: RegionPrice = self.create_region_price_model(dto=dto)
            region_price_serializer = RegionPriceSerializer(data=model_to_dict(model))
            region_price_serializer.is_valid(raise_exception=True)
            region_price = region_price_serializer.save()
            return region_price
        except Exception as e:
            logger.error(
                f"create_region_price 실패 e : {e} dto : {dto.__dict__}",
            )
            return False

    def create_region_price_model(self, dto) -> RegionPrice:
        return RegionPrice(
            region_id=dto.region.id,
            total_deal_price=dto.total_deal_price,
            total_jeonse_price=dto.total_jeonse_price,
            total_deal_price_per_pyung=dto.total_deal_price_per_pyung,
            total_jeonse_price_per_pyung=dto.total_jeonse_price_per_pyung,
            average_deal_price=dto.average_deal_price,
            average_jeonse_price=dto.average_jeonse_price,
            average_deal_price_per_pyung=dto.average_deal_price_per_pyung,
            average_jeonse_price_per_pyung=dto.average_jeonse_price_per_pyung,
            deal_date=dto.deal_date,
            deal_count=dto.deal_count,
            jeonse_count=dto.jeonse_count,
        )

    def get_region_prices(self, dto: GetRealEstatesOnMapDto = None):
        _q = RegionPrice.objects.select_related("region")

        """
        TODO
        * 통계용으로 deal_date filter 추가, 기본은 최근 n달치 정보 응답
        * si에서 세종시 중복 제거. orm 짜야 함
        select distinct sido
        from region
        where  sido !='' and sigungu='' and ubmyundong='';
        """

        if isinstance(dto, GetRealEstatesOnMapDto):
            logger.debug(dto.__dict__)
            if dto.zoom_level == RegionZoomLevelEnum.DONGRI.value:
                # dongri
                _q = _q.exclude(region__dongri="")
            elif dto.zoom_level == RegionZoomLevelEnum.UBMYUNDONG.value:
                # ubmyundong
                _q = _q.exclude(region__ubmyundong="").filter(region__dongri="")
            elif dto.zoom_level == RegionZoomLevelEnum.SIGUNGU.value:
                # sigungu
                _q = (
                    _q.exclude(region__sigungu="")
                    .filter(region__ubmyundong="")
                    .filter(region__dongri="")
                )
            elif dto.zoom_level == RegionZoomLevelEnum.SIDO.value:
                # sido
                _q = (
                    _q.exclude(region__sido="")
                    .filter(region__sigungu="")
                    .filter(region__ubmyundong="")
                    .filter(region__dongri="")
                )

            try:
                _q = _q.filter(
                    region__latitude__gte=dto.sw_lat,
                    region__latitude__lte=dto.ne_lat,
                    region__longitude__gte=dto.sw_lng,
                    region__longitude__lte=dto.ne_lng,
                )

                return _q.all()[:20]
            except Exception as e:
                logger.error(f"get_region_price 실패 e : {e}")
                return False
        else:
            try:
                return RegionPrice.objects.all()
            except Exception as e:
                logger.error(f"get_region_price 실패 e : {e}")
                return False

    def get_deals(self, dto: GetDealsDto = None):
        return (
            Deal.objects.select_related("real_estate")
            .filter(real_estate__id=dto.real_estate_id)
            .filter(deal_type=dto.deal_type)
            .all()
            .order_by("-deal_year", "-deal_month", "-deal_day")
        )

    def get_last_region_price(self):
        return RegionPrice.objects.order_by("-id").first()

    def get_last_deal(self):
        return Deal.objects.order_by("-id").first()
