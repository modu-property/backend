from typing import List, Optional, Union

from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.dto.get_real_estate_dto import (
    GetDealsDto,
    GetRealEstatesOnMapDto,
)
from real_estate.enum.deal_enum import DealTypesForDBEnum, DealTypesForQueryEnum
from real_estate.enum.real_estate_enum import (
    RegionZoomLevelEnum,
    RealEstateTypesForDBEnum,
    RealEstateTypesForQueryEnum,
)
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
    Q,
)
from django.db.models.functions import Concat
from real_estate.serializers import RegionPriceSerializer


class RealEstateRepository:
    @staticmethod
    def get_real_estate_all():
        return RealEstate.objects.all()

    @staticmethod
    def get_real_estate(real_estate_id: int) -> Optional[QuerySet[RealEstate]]:
        try:
            return RealEstate.objects.filter(id=real_estate_id).get()
        except Exception as e:
            logger.error(f"get_real_estate e : {e}")
            return None

    @staticmethod
    def get_real_estates(dto: CollectRegionPriceDto = None):
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

    @staticmethod
    def get_individual_real_estates(dto: GetRealEstatesOnMapDto):
        """
        시, 군, 구, 동이 아닌 개별 부동산 정보를 응답함
        """
        try:
            real_estates_and_deals = (
                Deal.objects.select_related("real_estate")
                .filter(
                    Q(
                        is_deal_canceled=False,
                        real_estate__latitude__gte=dto.sw_lat,
                        real_estate__latitude__lte=dto.ne_lat,
                        real_estate__longitude__gte=dto.sw_lng,
                        real_estate__longitude__lte=dto.ne_lng,
                        deal_type=dto.deal_type,
                    )
                    | Q(
                        is_deal_canceled=None,
                        real_estate__latitude__gte=dto.sw_lat,
                        real_estate__latitude__lte=dto.ne_lat,
                        real_estate__longitude__gte=dto.sw_lng,
                        real_estate__longitude__lte=dto.ne_lng,
                        deal_type=dto.deal_type,
                    )
                )
                .annotate(
                    deal_date=Concat(
                        "deal_year",
                        Value("-"),
                        "deal_month",
                        Value("-"),
                        "deal_day",
                        output_field=DateField(),
                    ),
                    name=F("real_estate__name"),
                    lot_number=F("real_estate__lot_number"),
                    address=F("real_estate__address"),
                    road_name_address=F("real_estate__road_name_address"),
                    build_year=F("real_estate__build_year"),
                    latitude=F("real_estate__latitude"),
                    longitude=F("real_estate__longitude"),
                    real_estate_type=F("real_estate__real_estate_type"),
                )
                .order_by("-deal_year", "-deal_month", "-deal_day")
            )
            return real_estates_and_deals[:150]
        except Exception as e:
            logger.error(f"get_individual_real_estates e : {e}")
            return False

    @staticmethod
    def bulk_create_regions(
        region_models: List[Region],
    ) -> Union[List[Region], bool]:
        try:
            result: List[Region] = Region.objects.bulk_create(region_models)
            return result
        except Exception as e:
            logger.error(f"bulk_create_regions 실패 e : {e}")
            return False

    @staticmethod
    def update_region(region: Region) -> bool:
        try:
            region.save()
            return True
        except Exception as e:
            logger.error(f"update_region 실패 e : {e}")
            return False

    @staticmethod
    def get_regions(sido: str = "") -> Union[QuerySet, bool]:
        _q = Region.objects
        if sido:
            return _q.filter(sido=sido)
        else:
            return _q.all()

    @staticmethod
    def get_regions_exclude_branch(sido: str):
        qs = Region.objects.values("sido", "regional_code").annotate(
            c=Count("id")
        )
        qs = qs.filter(sido=sido)
        regions = qs.exclude(sido__contains="출장소").exclude(sigungu="")
        return regions

    @staticmethod
    def get_region(
        sido: str = "",
        sigungu: str = "",
        ubmyundong: str = "",
        dongri: str = "",
    ):
        _q = Region.objects

        if dongri:
            _q = _q.filter(
                sido=sido, sigungu=sigungu, ubmyundong=ubmyundong, dongri=dongri
            )
        elif ubmyundong:
            _q = _q.filter(
                sido=sido, sigungu=sigungu, ubmyundong=ubmyundong, dongri=""
            )
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
            dto.region_id = dto.region.id
            region_price_serializer = RegionPriceSerializer(data=dto.__dict__)
            region_price_serializer.is_valid(raise_exception=True)
            region_price = region_price_serializer.save()
            return region_price
        except Exception as e:
            logger.error(
                f"create_region_price 실패 e : {e} dto : {dto.__dict__}",
            )
            return False

    @staticmethod
    def get_region_prices(dto: GetRealEstatesOnMapDto = None):
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
            if dto.zoom_level == RegionZoomLevelEnum.UBMYUNDONG.value:
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

    @staticmethod
    def get_deals(dto: GetDealsDto = None):
        return (
            Deal.objects.select_related("real_estate")
            .filter(real_estate__id=dto.real_estate_id)
            .filter(deal_type=dto.deal_type)
            .all()
            .order_by("-deal_year", "-deal_month", "-deal_day")
        )

    @staticmethod
    def get_deals_by_address_and_date(
        dto: CollectDealPriceOfRealEstateDto = None,
    ):
        deal_year = dto.year_month[:4]
        deal_month = dto.year_month[4:]
        return (
            Deal.objects.select_related("real_estate")
            .filter(real_estate__real_estate_type=dto.real_estate_type)
            .filter(deal_type=dto.deal_type)
            .filter(real_estate__regional_code=dto.regional_code)
            .filter(deal_year=deal_year)
            .filter(deal_month=deal_month)
            .all()
            .order_by("-deal_year", "-deal_month", "-deal_day")
        )

    @staticmethod
    def get_last_region_price():
        return RegionPrice.objects.order_by("-id").first()

    @staticmethod
    def get_last_deal():
        return Deal.objects.order_by("-id").first()

    @staticmethod
    def get_real_estates_by_regional_code_and_type(
        dto: CollectDealPriceOfRealEstateDto,
    ):
        _real_estate_type = (
            RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value
            if dto.real_estate_type
            == RealEstateTypesForQueryEnum.MULTI_UNIT_HOUSE.value
            else None
        )

        return list(
            RealEstate.objects.filter(
                regional_code=dto.regional_code,
                real_estate_type=_real_estate_type,
            ).all()
        )
