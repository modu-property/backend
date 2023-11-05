import os
import subprocess
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from property.models import Villa, VillaDeal


class Command(BaseCommand):
    help = "manticore search가 indexing할 데이터들을 insert하는 명령어"

    def run_indexer(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        subprocess.run(["bash", f"{dir_path}/run_indexer.sh"])

    def delete_villa(self):
        Villa.objects.all().delete()

    def delete_villa_deal(self):
        VillaDeal.objects.all().delete()

    def create_villa_and_villa_deal(self):
        villa1 = Villa(
            name="테스트빌라 1",
            build_year=1990,
            regional_code="11650",
            lot_number="서울특별시 서초구 사평대로53길 22 (반포동)",
            road_name_address="서울특별시 서초구 반포동 739",
            latitude="37.5054",
            longitude="127.0216",
            point=Point(37.5054, 127.0216),
        )

        villa1.save()

        villa_deal1 = VillaDeal(
            villa_id=villa1.id,
            deal_price=10000,
            deal_type="BROKERAGE_DEAL",
            deal_year=2023,
            land_area=100,
            deal_month=3,
            deal_day=21,
            area_for_exclusive_use=80,
            floor=3,
            is_deal_canceled=False,
            deal_canceld_date=None,
            area_for_exclusive_use_pyung="30.30",
            area_for_exclusive_use_price_per_pyung="330",
        )

        villa_deal1.save()

        villa2 = Villa(
            name="OAK 빌",
            build_year=1990,
            regional_code="11650",
            lot_number="서울특별시 서초구 사평대로53길 30 (반포동)",
            road_name_address="서울특별시 서초구 반포동 734-32 반포엠",
            latitude="37.5056",
            longitude="127.0215",
            point=Point(37.5056, 127.0215),
        )

        villa2.save()

        villa_deal2 = VillaDeal(
            villa_id=villa2.id,
            deal_price=20000,
            deal_type="BROKERAGE_DEAL",
            deal_year=2023,
            land_area=200,
            deal_month=12,
            deal_day=30,
            area_for_exclusive_use=150,
            floor=5,
            is_deal_canceled=False,
            deal_canceld_date=None,
            area_for_exclusive_use_pyung="60.60",
            area_for_exclusive_use_price_per_pyung="329.99",
        )

        villa_deal2.save()

        villa3 = Villa(
            name="봉은사로 빌라",
            build_year=1990,
            regional_code="11650",
            lot_number="서울특별시 강남구 논현동 175-19",
            road_name_address="서울특별시 강남구 봉은사로25길 34 (논현동)",
            latitude="37.5094",
            longitude="127.0321",
            point=Point(37.5094, 127.0321),
        )

        villa3.save()

        villa_deal3 = VillaDeal(
            villa_id=villa3.id,
            deal_price=30000,
            deal_type="BROKERAGE_DEAL",
            deal_year=2022,
            land_area=150,
            deal_month=1,
            deal_day=1,
            area_for_exclusive_use=130,
            floor=2,
            is_deal_canceled=False,
            deal_canceld_date=None,
            area_for_exclusive_use_pyung="60.60",
            area_for_exclusive_use_price_per_pyung="329.99",
        )

        villa_deal3.save()

        villa4 = Villa(
            name="지산로얄빌라",
            build_year=1990,
            regional_code="21070",
            lot_number="부산광역시 남구 대연동 1724-1",
            road_name_address="부산광역시 남구 유엔로157번나길 48 (대연동, 지산로얄빌라)",
            latitude="35.133",
            longitude="129.0959",
            point=Point(35.133, 129.0959),
        )

        villa4.save()

        villa_deal4 = VillaDeal(
            villa_id=villa4.id,
            deal_price=30000,
            deal_type="BROKERAGE_DEAL",
            deal_year=2022,
            land_area=150,
            deal_month=1,
            deal_day=1,
            area_for_exclusive_use=130,
            floor=2,
            is_deal_canceled=False,
            deal_canceld_date=None,
            area_for_exclusive_use_pyung="60.60",
            area_for_exclusive_use_price_per_pyung="329.99",
        )

        villa_deal4.save()

    def handle(self, *args, **options):
        self.delete_villa_deal()
        self.delete_villa()
        self.create_villa_and_villa_deal()
        self.run_indexer()
