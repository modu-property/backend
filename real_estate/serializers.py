from decimal import Decimal

from django.contrib.gis.geos import Point
from rest_framework import serializers
from real_estate.enum.deal_enum import DEAL_TYPES
from real_estate.enum.real_estate_enum import RealEstateTypesForQueryEnum
from real_estate.models import Deal, RealEstate, Region, RegionPrice


class RealEstateSerializer(serializers.ModelSerializer):
    """
    bulk_create를 할 때는 SerializerMethodField가 동작하지 않으므로 직접 메서드를 호출해서 수정함.
    """

    이름 = serializers.CharField(source="name")
    건축년도 = serializers.IntegerField(source="build_year")
    지역코드 = serializers.CharField(source="regional_code")
    지번 = serializers.CharField(source="lot_number")
    road_name_address = serializers.CharField()
    address = serializers.CharField()
    real_estate_type = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = RealEstate
        geo_field = "point"
        fields = (
            "이름",
            "건축년도",
            "지역코드",
            "지번",
            "road_name_address",
            "address",
            "real_estate_type",
            "latitude",
            "longitude",
            "point",
        )

    # def get_organized_data(self, deal_price_of_real_estates):
    def get_organized_data(self, deal_price_of_real_estates):
        result = []
        for (
            _,
            deal_price_of_real_estate,
        ) in deal_price_of_real_estates.iterrows():
            if self._already_exist_then_skip(deal_price_of_real_estate):
                continue

            deal_price_of_real_estate = dict(deal_price_of_real_estate)

            self._set_name(deal_price_of_real_estate)

            self._set_address(deal_price_of_real_estate)

            address_info = deal_price_of_real_estate.get("address_info")

            deal_price_of_real_estate.update(
                {
                    "road_name_address": address_info["road_name_address"],
                    "address": address_info["address"],
                    "latitude": address_info["latitude"],
                    "longitude": address_info["longitude"],
                    "point": Point(
                        float(address_info["latitude"]),
                        float(address_info["longitude"]),
                    ),
                    "real_estate_type": self.context.get("real_estate_type"),
                }
            )

            result.append(deal_price_of_real_estate)
        return result

    def _already_exist_then_skip(self, deal_price_of_real_estate):
        unique_key = f"{deal_price_of_real_estate.get('지역코드')}{deal_price_of_real_estate.get('지번')}"
        unique_keys = self.context.get("unique_keys")
        if unique_key in unique_keys:
            return True
        unique_keys[unique_key] = None
        return False

    def _set_address(self, deal_price_of_real_estate):
        dong = deal_price_of_real_estate.get("법정동")
        lot_number = deal_price_of_real_estate.get("지번")
        query = f"{dong} {lot_number}"
        address_converter_util = self.context.get("address_converter_util")
        if not address_converter_util.convert_address(query=query):
            raise serializers.ValidationError(
                "address_converter_util failed 주소 정보가 없음"
            )
        address_info = address_converter_util.get_address()
        deal_price_of_real_estate["address_info"] = address_info

    def _set_name(self, deal_price_of_real_estate):
        if "연립다세대" in deal_price_of_real_estate:
            deal_price_of_real_estate["이름"] = deal_price_of_real_estate.pop(
                "연립다세대"
            )


class DealSerializer(serializers.ModelSerializer):
    area_for_exclusive_use_pyung = serializers.SerializerMethodField(
        "convert_square_meter_to_pyung"
    )
    area_for_exclusive_use_price_per_pyung = serializers.SerializerMethodField(
        "calc_price_per_pyung"
    )
    is_deal_canceled = serializers.SerializerMethodField(
        "calc_is_deal_canceled"
    )
    floor = serializers.SerializerMethodField("stringify_floor")

    # TODO : 해제사유 등은 Deal 모델에 넣어야 함
    # is_deal_canceled = serializers.BooleanField()
    # deal_canceled_date = serializers.DateField(allow_null=True)

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.pyung = None
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
            # "해제여부",
            # "해제사유발생일",
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

    @staticmethod
    def calc_is_deal_canceled(instance) -> bool:
        if instance.is_deal_canceled == "O":
            return True
        return False

    def stringify_floor(self, instance) -> str:
        self.floor = str(instance.floor)
        return self.floor

    # self._set_deal_canceled_date(deal_price_of_real_estate)
    #
    # self._set_is_deal_canceled(deal_price_of_real_estate)

    # def _set_is_deal_canceled(self, instance):
    #     if not instance.get("해제여부"):
    #         instance["is_deal_canceled"] = False

    # def _set_deal_canceled_date(self, instance):
    #     if instance.get("해제사유발생일"):
    #         deal_canceled_date = instance.get("해제사유발생일")
    #         y, m, d = deal_canceled_date.split(".")
    #         y = f"20{y}"
    #
    #         instance.pop("해제사유발생일")
    #         instance["deal_canceled_date"] = f"{y}-{m}-{d}"
    #     else:
    #         instance["deal_canceled_date"] = None


class GetRealEstateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)


class GetRealEstateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstate
        exclude = ("point",)


class GetRealEstatesOnSearchRequestSerializer(serializers.Serializer):
    deal_type = serializers.ChoiceField(choices=DEAL_TYPES)
    keyword = serializers.CharField()
    real_estate_search_limit = serializers.IntegerField(
        min_value=15, max_value=50
    )


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
    sw_lat = serializers.FloatField()
    sw_lng = serializers.FloatField()
    ne_lat = serializers.FloatField()
    ne_lng = serializers.FloatField()
    zoom_level = serializers.IntegerField(min_value=1, max_value=9)


class GetRealEstatesOnMapResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(
        max_length=30, allow_blank=True, allow_null=True
    )
    lot_number = serializers.CharField(
        max_length=50, allow_blank=False, allow_null=False
    )
    address = serializers.CharField(
        max_length=50, allow_blank=True, allow_null=True
    )
    road_name_address = serializers.CharField(
        max_length=50, allow_blank=True, allow_null=True
    )
    real_estate_type = serializers.ChoiceField(
        choices=RealEstateTypesForQueryEnum
    )
    build_year = serializers.IntegerField()
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
            "regional_code",
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


class GetRealEstatesAndRegionsOnSearchResponseSerializer(
    serializers.Serializer
):
    regions = GetRegionsOnSearchResponseSerializer(many=True, required=False)
    real_estates = GetRealEstatesOnSearchResponseSerializer(
        many=True, required=False
    )


class GetDealsRequestSerializer(serializers.Serializer):
    real_estate_id = serializers.IntegerField()
    page = serializers.IntegerField()
    deal_type = serializers.ChoiceField(choices=DEAL_TYPES)


class DealDictSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    deal_price = serializers.CharField()
    brokerage_type = serializers.CharField()
    deal_year = serializers.IntegerField()
    land_area = serializers.CharField()
    deal_month = serializers.IntegerField()
    deal_day = serializers.IntegerField()
    area_for_exclusive_use = serializers.CharField()
    floor = serializers.CharField()
    is_deal_canceled = serializers.BooleanField()
    deal_canceled_date = serializers.DateField(allow_null=True)
    area_for_exclusive_use_pyung = serializers.DecimalField(
        max_digits=10, decimal_places=2
    )
    area_for_exclusive_use_price_per_pyung = serializers.DecimalField(
        max_digits=10, decimal_places=2
    )
    deal_type = serializers.CharField()
    real_estate_id = serializers.IntegerField()
