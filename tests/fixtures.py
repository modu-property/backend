import jwt
import datetime
import pytest

from modu_property.test_settings import SECRET_KEY
from property.models import Villa


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
    villa = Villa(
        deal_price=111111,
        deal_type="DIRECT_DEAL",
        build_year=2020,
        deal_year=2023,
        land_area=11,
        dong="논현동",
        name="그냥빌라",
        deal_month=1,
        deal_day=21,
        area_for_exclusive_use=13,
        lot_number="11-11",
        regional_code=123,
        floor=1,
        is_deal_canceled=False,
        deal_canceld_date=None,
        broker_address=None,
        road_name_address="주흥길 31-11",
        latitude="12.2312",
        longitude="21.423",
        pyung="12",
        price_per_pyung="1242000",
    )
    villa.save()

    return villa
