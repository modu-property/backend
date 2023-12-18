import datetime
from pandas import DataFrame
import pytest
from real_estate.models import Deal, RealEstate, MonthlyRent
from django.contrib.gis.geos import Point


@pytest.fixture
def create_real_estate():
    def _create_real_estate(
        name: str,
        build_year: int,
        regional_code: str,
        lot_number: str,
        road_name_address: str,
        latitude: str,
        longitude: str,
        point: Point,
    ):
        real_estate = RealEstate(
            name=name,
            build_year=build_year,
            regional_code=regional_code,
            lot_number=lot_number,
            road_name_address=road_name_address,
            latitude=latitude,
            longitude=longitude,
            point=point,
        )
        real_estate.save()
        return real_estate

    return _create_real_estate


@pytest.fixture
def create_deal():
    def _create_deal(
        real_estate_id: int,
        deal_price: int,
        deal_type: str,
        deal_year: int,
        land_area: str,
        deal_month: int,
        deal_day: int,
        area_for_exclusive_use: str,
        floor: str,
        is_deal_canceled: bool,
        deal_canceled_date: datetime,
        area_for_exclusive_use_pyung: str,
        area_for_exclusive_use_price_per_pyung: str,
        type: str,
    ):
        deal = Deal(
            real_estate_id=real_estate_id,
            deal_price=deal_price,
            deal_type=deal_type,
            deal_year=deal_year,
            land_area=land_area,
            deal_month=deal_month,
            deal_day=deal_day,
            area_for_exclusive_use=area_for_exclusive_use,
            floor=floor,
            is_deal_canceled=is_deal_canceled,
            deal_canceled_date=deal_canceled_date,
            area_for_exclusive_use_pyung=area_for_exclusive_use_pyung,
            area_for_exclusive_use_price_per_pyung=area_for_exclusive_use_price_per_pyung,
            type=type,
        )
        deal.save()
        return deal

    return _create_deal


@pytest.fixture
def create_monthly_rent():
    def _create_monthly_rent(deal_id: int, price: int):
        monthly_rent = MonthlyRent(deal_id=deal_id, price=price)
        monthly_rent.save()
        return monthly_rent

    return _create_monthly_rent


@pytest.fixture
def mock_collect_deal_price_of_real_estate():
    dct = {
        "지역코드": {0: "11110", 1: "11110", 2: "11110"},
        "법정동": {0: "청운동", 1: "신교동", 2: "필운동"},
        "지번": {0: "134-2", 1: "15-1", 2: "26"},
        "연립다세대": {0: "풍림팍사이드빌라", 1: "(15-1)", 2: "우인빌라"},
        "건축년도": {0: 1997, 1: 1998, 2: 2001},
        "층": {0: 2, 1: 2, 2: 3},
        "대지권면적": {0: 37.902, 1: 22.75, 2: 21.55},
        "전용면적": {0: 53.83, 1: 59.88, 2: 50.55},
        "년": {0: 2020, 1: 2020, 2: 2020},
        "월": {0: 1, 1: 1, 2: 1},
        "일": {0: 20, 1: 11, 2: 6},
        "거래금액": {0: 28000, 1: 40000, 2: 31000},
        "거래유형": {0: None, 1: None, 2: None},
        "중개사소재지": {0: None, 1: None, 2: None},
        "해제사유발생일": {0: None, 1: None, 2: None},
        "해제여부": {0: None, 1: None, 2: None},
    }

    return DataFrame.from_dict(dct)
