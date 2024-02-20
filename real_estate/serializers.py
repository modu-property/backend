from decimal import Decimal
from rest_framework import serializers
from real_estate.enum.deal_enum import DEAL_TYPES
from real_estate.models import Deal, RealEstate, Region, RegionPrice


class RealEstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstate
        fields = (
            "name",
            "build_year",
            "regional_code",
            "lot_number",
            "road_name_address",
            "address",
            "real_estate_type",
            "latitude",
            "longitude",
            "point",
        )


class DealSerializer(serializers.ModelSerializer):
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
            "brokerage_type",
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
            "deal_type",
            "real_estate_id",
        )

    def convert_square_meter_to_pyung(self, instance) -> Decimal:
        self.pyung = round(
            Decimal(instance.area_for_exclusive_use) / Decimal(3.305785), 2
        )
        return self.pyung

    def calc_price_per_pyung(self, instance) -> Decimal:
        return round(instance.deal_price / self.pyung, 2)

    def calc_is_deal_canceled(self, instance) -> bool:
        if instance.is_deal_canceled == "O":
            return True
        return False

    def stringify_floor(self, instance) -> str:
        self.floor = str(instance.floor)
        return self.floor


class GetRealEstateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)


class GetRealEstateResponseSerializer(serializers.ModelSerializer):
    deals = DealSerializer(many=True)

    class Meta:
        model = RealEstate
        exclude = ("point",)


class GetRealEstatesOnSearchRequestSerializer(serializers.Serializer):
    deal_type = serializers.ChoiceField(choices=DEAL_TYPES)
    keyword = serializers.CharField()
    limit = serializers.IntegerField(min_value=1, max_value=300)


class GetRealEstatesOnSearchResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    lot_number = serializers.CharField(max_length=30)
    name = serializers.CharField(max_length=30)
    road_name_address = serializers.CharField(max_length=30, allow_blank=True)
    address = serializers.CharField(max_length=30)
    real_estate_type = serializers.CharField(max_length=20)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class GetRealEstatesOnMapRequestSerializer(serializers.Serializer):
    deal_type = serializers.ChoiceField(choices=DEAL_TYPES)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    sw_lat = serializers.FloatField()
    sw_lng = serializers.FloatField()
    ne_lat = serializers.FloatField()
    ne_lng = serializers.FloatField()
    zoom_level = serializers.IntegerField(max_value=6, min_value=0)


class GetRealEstatesOnMapResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    latitude = serializers.CharField(max_length=20)
    longitude = serializers.CharField(max_length=20)
    deal_price = serializers.IntegerField()
    area_for_exclusive_use_pyung = serializers.CharField(max_length=6)
    area_for_exclusive_use_price_per_pyung = serializers.CharField(max_length=8)
    real_estate_type = serializers.CharField(max_length=20)
    deal_date = serializers.DateField()


class RegionPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionPrice
        fields = (
            "total_deal_price",
            "total_jeonse_price",
            "average_deal_price",
            "average_jeonse_price",
            "average_deal_price_per_pyung",
            "average_jeonse_price_per_pyung",
            "deal_date",
            "region",
            "deal_count",
            "jeonse_count",
            "total_deal_price_per_pyung",
            "total_jeonse_price_per_pyung",
        )


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = (
            "sido",
            "sigungu",
            "ubmyundong",
            "dongri",
            "latitude",
            "longitude",
        )


class GetRegionsOnMapResponseSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = RegionPrice
        fields = "__all__"


class GetRegionsOnSearchResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sido = serializers.CharField(max_length=10, allow_blank=True)
    sigungu = serializers.CharField(max_length=15, allow_blank=True)
    ubmyundong = serializers.CharField(max_length=20, allow_blank=True)
    dongri = serializers.CharField(max_length=20, allow_blank=True)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class GetRealEstatesAndRegionsOnSearchResponseSerializer(serializers.Serializer):
    regions = GetRegionsOnSearchResponseSerializer(many=True, required=False)
    real_estates = GetRealEstatesOnSearchResponseSerializer(many=True, required=False)
