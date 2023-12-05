import jwt
import datetime
import pytest
from accounts.models import User

from modu_property.test_settings import SECRET_KEY
from real_estate.models import Deal, RealEstate, MonthlyRent
from django.contrib.gis.geos import Point
from django.contrib.auth.hashers import make_password


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
def create_user():
    def _create_user(username: str, password: str):
        encrypted_password = make_password(str(password))
        user = User(username=username, password=encrypted_password)

        user.save()
        return user

    return _create_user


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
