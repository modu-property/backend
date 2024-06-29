from typing import List, Optional, Union
from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto
from real_estate.dto.get_real_estate_dto import (
    GetDealsDto,
    GetRealEstatesOnMapDto,
)
from real_estate.enum.real_estate_enum import RegionZoomLevelEnum, MapLimitEnum
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
    Max,
    CharField,
    Window,
    FilteredRelation,
)
from django.db.models.functions import Concat, RowNumber, Coalesce
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
        개별 부동산(real_estate)의 최신 거래(deal)을 1개만 join 해서 응답함.
        """
        try:
            qs = (
                RealEstate.objects.annotate(
                    latest_deal=FilteredRelation(
                        "deals",
                        condition=Q(
                            deals=Subquery(
                                Deal.objects.filter(
                                    Q(deal_year__gte=dto.start_year)
                                    & Q(deal_month__gte=dto.start_month)
                                    & Q(deal_year__lte=dto.end_year)
                                    & Q(deal_month__lte=dto.end_month)
                                    & Q(real_estate=OuterRef("id"))
                                )
                                .order_by(
                                    "-deal_year", "-deal_month", "-deal_day"
                                )
                                .values("id")[:1]
                            ),
                        ),
                    ),
                )
                .filter(latest_deal__isnull=False)
                .select_related("latest_deal")
            )

            real_estates = list(qs)

            return real_estates[: MapLimitEnum.REAL_ESTATES.value]
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
            if (
                RegionZoomLevelEnum.UBMYUNDONG_MIN.value
                <= dto.zoom_level
                <= RegionZoomLevelEnum.UBMYUNDONG_MAX.value
            ):
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
    def get_last_region_price():
        return RegionPrice.objects.order_by("-id").first()

    @staticmethod
    def get_last_deal():
        return Deal.objects.order_by("-id").first()
