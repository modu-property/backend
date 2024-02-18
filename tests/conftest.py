import datetime
from pandas import DataFrame
import pandas
import pytest
from real_estate.models import Deal, RealEstate, MonthlyRent, Region
from django.contrib.gis.geos import Point
import os
from django.db import connections

import jwt
import pytest

from modu_property.settings.test_settings import SECRET_KEY
from django.contrib.auth.hashers import make_password
from accounts.models import User


@pytest.fixture()
def create_real_estate():
    def _create_real_estate(
        name: str,
        build_year: int,
        regional_code: str,
        lot_number: str,
        road_name_address: str,
        address: str,
        real_estate_type: str,
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
            address=address,
            real_estate_type=real_estate_type,
            latitude=latitude,
            longitude=longitude,
            point=point,
        )
        real_estate.save()
        return real_estate

    return _create_real_estate


@pytest.fixture()
def create_deal():
    def _create_deal(
        real_estate_id: int,
        deal_price: int,
        brokerage_type: str,
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
        deal_type: str,
    ):
        deal = Deal(
            real_estate_id=real_estate_id,
            deal_price=deal_price,
            brokerage_type=brokerage_type,
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
            deal_type=deal_type,
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
        "층": {0: "2", 1: "2", 2: "3"},
        "대지권면적": {0: "37.902", 1: "22.75", 2: "21.55"},
        "전용면적": {0: "53.83", 1: "59.88", 2: "50.55"},
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


def get_file_path(file_name: str):
    dir_path = "tests"
    return os.path.join(os.getcwd(), dir_path, file_name)


@pytest.fixture
def insert_regional_codes():
    def _insert_regional_codes(start: int = 0, end: int = 30000):
        connection = connections["default"]

        path: str = get_file_path(file_name="insert_regional_codes.sql")

        # Read SQL commands from the file
        with open(path, "r") as file:
            sql_commands = file.read()

        # Split the SQL commands if there are multiple commands
        commands = sql_commands.split(";")[start : end + 1]

        # Execute each SQL command
        with connection.cursor() as cursor:
            for command in commands:
                if command.strip():
                    cursor.execute(command)

    return _insert_regional_codes


@pytest.fixture
def get_dongs():
    def _get_dongs(count: int = 10) -> DataFrame:
        path: str = get_file_path(file_name="files/dong.csv")

        df: pandas.DataFrame = pandas.read_csv(
            filepath_or_buffer=path, nrows=count, keep_default_na=False
        )

        return df

    return _get_dongs


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
def create_region():
    def _create_region(
        sido: str = "서울특별시",
        regional_code: str = "11000",
        sigungu: str = "",
        ubmyundong: str = "",
        dongri: str = "",
        latitude: str = "37.566826004661",
        longitude: str = "126.978652258309",
    ):
        region = Region(
            sido=sido,
            regional_code=regional_code,
            sigungu=sigungu,
            ubmyundong=ubmyundong,
            dongri=dongri,
            latitude=latitude,
            longitude=longitude,
        )

        region.save()
        return region

    return _create_region
