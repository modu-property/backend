from decimal import Decimal
from rest_framework import serializers
from real_estate.models import Deal, RealEstate


class RealEstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstate
        fields = (
            "name",
            "build_year",
            "regional_code",
            "lot_number",
            "road_name_address",
            "latitude",
            "longitude",
            "point",
        )


class DealSerializer(serializers.ModelSerializer):
    deal_type = serializers.SerializerMethodField()
    area_for_exclusive_use_pyung = serializers.SerializerMethodField(
        "convert_square_meter_to_pyung"
    )
    area_for_exclusive_use_price_per_pyung = serializers.SerializerMethodField(
        "calc_price_per_pyung"
    )
    is_deal_canceled = serializers.SerializerMethodField("calc_is_deal_canceled")
    floor = serializers.SerializerMethodField("stringify_floor")

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.area_for_exclusive_use_pyung = None

    class Meta:
        model = Deal
        fields = (
            "id",
            "deal_price",
            "deal_type",
            "deal_year",
            "land_area",
            "deal_month",
            "deal_day",
            "area_for_exclusive_use",
            "floor",
            "is_deal_canceled",
            "deal_canceled_date",
            "area_for_exclusive_use_pyung",
            "area_for_exclusive_use_price_per_pyung",
            "type",
            "real_estate_id",
        )

    def get_deal_type(self, instance):
        if not instance.deal_type:
            return None

    def convert_square_meter_to_pyung(self, instance):
        self.pyung = round(
            Decimal(instance.area_for_exclusive_use) / Decimal(3.305785), 2
        )
        return self.pyung

    def calc_price_per_pyung(self, instance) -> Decimal:
        return round(instance.deal_price / self.pyung, 2)

    def calc_is_deal_canceled(self, instance):
        if instance.is_deal_canceled == "O":
            return True
        return False

    def stringify_floor(self, instance):
        self.floor = str(instance.floor)
        return self.floor


class GetRealEstateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    TYPE_CHOICES = (
        ("deal", "deal"),
        ("jeonse", "jeonse"),
        ("monthly_rent", "monthly_rent"),
    )
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    zoom_level = serializers.IntegerField(max_value=6, min_value=0)
    keyword = serializers.CharField(allow_blank=True)


class GetRealEstatesOnSearchTabResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    lot_number = serializers.CharField(max_length=30)
    name = serializers.CharField(max_length=30)
    road_name_address = serializers.CharField(max_length=30)


class GetRealEstatesOnMapResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    latitude = serializers.CharField(max_length=20)
    longitude = serializers.CharField(max_length=20)
    area_for_exclusive_use_pyung = serializers.CharField(max_length=6)
    area_for_exclusive_use_price_per_pyung = serializers.CharField(max_length=8)


class GetRealEstateByIdSerializer(serializers.ModelSerializer):
    deals = DealSerializer(many=True)

    class Meta:
        model = RealEstate
        fields = "__all__"
