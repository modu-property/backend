import jwt
import datetime
import pytest

from modu_property.test_settings import SECRET_KEY
from property.models import Villa, VillaDeal
from django.contrib.gis.geos import Point


@pytest.fixture
def get_jwt():
    return jwt.encode(
        {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            # "user_id": 1,
        },
        SECRET_KEY,
        algorithm="HS256",
    )


@pytest.fixture
def create_villa():
    def _create_villa(
        name: str,
        build_year: int,
        regional_code: str,
        lot_number: str,
        road_name_address: str,
        latitude: str,
        longitude: str,
        point: Point,
    ):
        villa = Villa(
            name=name,
            build_year=build_year,
            regional_code=regional_code,
            lot_number=lot_number,
            road_name_address=road_name_address,
            latitude=latitude,
            longitude=longitude,
            point=point,
        )
        villa.save()
        return villa

    return _create_villa


@pytest.fixture
def create_villa_deal():
    def _create_villa_deal(
        villa_id: int,
        deal_price: int,
        deal_type: str,
        deal_year: int,
        land_area: str,
        deal_month: int,
        deal_day: int,
        area_for_exclusive_use: str,
        floor: str,
        is_deal_canceled: bool,
        deal_canceld_date: datetime,
        area_for_exclusive_use_pyung: str,
        area_for_exclusive_use_price_per_pyung: str,
    ):
        villa_deal = VillaDeal(
            villa_id=villa_id,
            deal_price=deal_price,
            deal_type=deal_type,
            deal_year=deal_year,
            land_area=land_area,
            deal_month=deal_month,
            deal_day=deal_day,
            area_for_exclusive_use=area_for_exclusive_use,
            floor=floor,
            is_deal_canceled=is_deal_canceled,
            deal_canceld_date=deal_canceld_date,
            area_for_exclusive_use_pyung=area_for_exclusive_use_pyung,
            area_for_exclusive_use_price_per_pyung=area_for_exclusive_use_price_per_pyung,
        )
        villa_deal.save()
        return villa_deal

    return _create_villa_deal
