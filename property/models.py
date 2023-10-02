from django.db import models

from modu_property.common.models.models import DateTimeFields


DEAL_TYPES = (
    ("BROKERAGE_DEAL", "중개거래"),
    ("DIRECT_DEAL", "직거래")
)

class Villa(DateTimeFields):
    id = models.AutoField(primary_key=True)
    deal_price = models.PositiveIntegerField(help_text="거래금액(거래금액(만원))", null=False, blank=False)
    deal_type = models.CharField(help_text="중개/직거래(거래유형)", null=True, blank=True, choices=DEAL_TYPES, max_length=14)
    build_year = models.SmallIntegerField(help_text="건축년도", null=False, blank=False)
    deal_year = models.SmallIntegerField(help_text="계약년도(년)", null=False, blank=False)
    land_area = models.CharField(help_text="대지권면적", null=False, blank=False, max_length=10)
    dong = models.CharField(help_text="동", null=False, blank=False, max_length=10)
    name = models.CharField(help_text="연립/다세대 이름", null=False, blank=False, max_length=30)
    deal_month = models.SmallIntegerField(help_text="계약 월", null=False, blank=False)
    deal_day = models.SmallIntegerField(help_text="계약 일", null=False, blank=False)
    area_for_exclusive_use = models.CharField(help_text="전용면적(제곱미터)", null=False, blank=False, max_length=7)
    lot_number = models.CharField(help_text="지번(구획마다 부여된 땅 번호, 서울특별시 서초구 반포동 1-1)", null=False, blank=False, max_length=30)
    regional_code = models.CharField(help_text="지역코드", null=False, blank=False, max_length=5)
    floor = models.CharField(help_text="층", null=False, blank=False, max_length=2)
    is_deal_canceled = models.BooleanField(help_text="해제여부(거래계약이 무효, 취소, 해제)", null=False, blank=False)
    deal_canceld_date = models.DateField(help_text="해제사유 발생일", null=True, blank=True)
    broker_address = models.CharField(help_text="중개업소 주소(중개사소재지)", null=True, blank=True, max_length=30)
    road_name_address = models.CharField(help_text="도로명 주소", null=False, blank=False, max_length=30)
    latitude = models.CharField(help_text="위도", null=False, blank=False, max_length=10)
    longitude = models.CharField(help_text="경도", null=False, blank=False, max_length=10)
    pyung = models.CharField(help_text="평", null=False, blank=False, max_length=6)
    price_per_pyung = models.CharField(help_text="평당가", null=False, blank=False, max_length=8)
