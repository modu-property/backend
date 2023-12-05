from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations
from modu_property.common.models.models import DateTimeFields

DEAL_TYPES = (("BROKERAGE_DEAL", "중개거래"), ("DIRECT_DEAL", "직거래"))
TYPES = (("DEAL", "매매"), ("JEONSE", "전세"), ("MONTHLY_RENT", "월세"))


class Migration(migrations.Migration):
    operations = [CreateExtension("postgis")]


class RealEstate(gis_models.Model):
    class Meta:
        db_table = "real_estate"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(help_text="부동산 이름", null=True, blank=True, max_length=30)
    build_year = models.SmallIntegerField(help_text="건축년도", null=False, blank=False)
    regional_code = models.CharField(
        help_text="지역코드", null=False, blank=False, max_length=6
    )
    lot_number = models.CharField(
        help_text="지번(구획마다 부여된 땅 번호, 서울특별시 서초구 반포동 1-1)",
        null=False,
        blank=False,
        max_length=50,
    )
    road_name_address = models.CharField(
        help_text="도로명 주소", null=False, blank=False, max_length=50
    )
    latitude = models.CharField(help_text="위도", null=False, blank=False, max_length=20)
    longitude = models.CharField(help_text="경도", null=False, blank=False, max_length=20)
    point = gis_models.PointField(geography=True, null=False, blank=False)


class Deal(DateTimeFields):
    class Meta:
        db_table = "deal"

    id = models.BigAutoField(primary_key=True)

    deal_price = models.PositiveIntegerField(
        help_text="거래금액(전월세 보증금)", null=False, blank=False
    )
    deal_type = models.CharField(
        help_text="중개/직거래(거래유형)",
        null=True,
        blank=True,
        choices=DEAL_TYPES,
        max_length=14,
    )
    deal_year = models.SmallIntegerField(help_text="계약년도(년)", null=False, blank=False)
    land_area = models.CharField(
        help_text="대지권면적", null=False, blank=False, max_length=10
    )
    deal_month = models.SmallIntegerField(help_text="계약 월", null=False, blank=False)
    deal_day = models.SmallIntegerField(help_text="계약 일", null=False, blank=False)
    area_for_exclusive_use = models.CharField(
        help_text="전용면적(제곱미터)", null=False, blank=False, max_length=10
    )
    floor = models.CharField(help_text="층", null=False, blank=False, max_length=3)
    is_deal_canceled = models.BooleanField(
        help_text="해제여부(거래계약이 무효, 취소, 해제)", null=False, blank=False
    )
    deal_canceled_date = models.DateField(help_text="해제사유 발생일", null=True, blank=True)
    area_for_exclusive_use_pyung = models.CharField(
        help_text="전용면적(평)", null=False, blank=False, max_length=7
    )
    area_for_exclusive_use_price_per_pyung = models.CharField(
        help_text="전용면적 평당가", null=False, blank=False, max_length=8
    )
    type = models.CharField(
        help_text="유형(DEAL(매매), JEONSE(전세), MONTHLY_RENT(월세))",
        null=False,
        blank=False,
        max_length=13,
    )

    real_estate = models.ForeignKey(
        "RealEstate",
        related_name="deal",
        on_delete=models.DO_NOTHING,
    )


class MonthlyRent(DateTimeFields):
    class Meta:
        db_table = "monthly_rent"

    deal = models.OneToOneField(
        Deal, primary_key=True, help_text="기본키, 거래 외래키", on_delete=models.CASCADE
    )
    price = models.PositiveIntegerField(
        help_text="반전세의 월세, 월세", null=False, blank=False
    )
