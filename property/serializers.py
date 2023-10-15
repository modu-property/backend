from decimal import Decimal
from rest_framework import serializers
from rest_framework.fields import empty

from property.models import Villa


class VillaSerializer(serializers.ModelSerializer):
    deal_price = serializers.SerializerMethodField()
    deal_type = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    pyung = serializers.SerializerMethodField("convert_square_meter_to_pyung")
    price_per_pyung = serializers.SerializerMethodField("calc_price_per_pyung")
    is_deal_canceled = serializers.SerializerMethodField("calc_is_deal_canceled")
    # road_name_address = serializers.SerializerMethodField("get_road_name_address")

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.deal_price = None
        self.pyung = None

    class Meta:
        model = Villa
        fields = (
            "deal_price",
            "deal_type",
            "build_year",
            "deal_year",
            "land_area",
            "dong",
            "name",
            "deal_month",
            "deal_day",
            "area_for_exclusive_use",
            "lot_number",
            "regional_code",
            "floor",
            "is_deal_canceled",
            "deal_canceld_date",
            "broker_address",
            "road_name_address",
            "latitude",
            "longitude",
            "pyung",
            "price_per_pyung",
        )

    def get_deal_price(self, instance):
        self.deal_price = int(instance.deal_price.replace(",", ""))
        return self.deal_price

    def get_deal_type(self, instance):
        if not instance.deal_type:
            return None

    def get_latitude(self, instance):
        latitude = instance.latitude
        integer, _decimal = instance.latitude.split(".")
        if len(_decimal) > 6:
            latitude = integer + "." + _decimal[:6]
        return latitude

    def get_longitude(self, instance):
        longitude = instance.longitude
        integer, _decimal = instance.longitude.split(".")
        if len(_decimal) > 6:
            longitude = integer + "." + _decimal[:6]
        return longitude

    def convert_square_meter_to_pyung(self, instance):
        self.pyung = round(
            Decimal(instance.area_for_exclusive_use) / Decimal(3.305785), 2
        )
        return self.pyung

    def calc_price_per_pyung(self, instance) -> Decimal:
        return round(self.deal_price / self.pyung, 2)

    def calc_is_deal_canceled(self, instance):
        if instance.is_deal_canceled == "O":
            return True
        return False


class GetVillaRequestSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        ("deal", "deal"),
        ("jeonse", "jeonse"),
        ("monthly_rent", "monthly_rent"),
    )
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    latitude = serializers.CharField(max_length=10)
    longitude = serializers.CharField(max_length=10)
    zoom_level = serializers.IntegerField()
    keyword = serializers.CharField(allow_blank=True)


class GetVillasOnSearchTabResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    lot_number = serializers.CharField(max_length=30)
    dong = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=30)
    road_name_address = serializers.CharField(max_length=30)
