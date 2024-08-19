from decimal import Decimal

from django.contrib.gis.geos import Point
from rest_framework import serializers
from real_estate.enum.deal_enum import (
    DEAL_TYPES,
    DealTypesForDBEnum,
    BrokerageTypesEnum,
)
from real_estate.enum.real_estate_enum import (
    RealEstateTypesForQueryEnum,
    RealEstateKeyEnum,
)
from real_estate.models import Deal, RealEstate, Region, RegionPrice
from modu_property.utils.loggers import file_logger


class RealEstateSerializer(serializers.ModelSerializer):
    """
    bulk_create를 할 때는 SerializerMethodField가 동작하지 않으므로 직접 메서드를 호출해서 수정함.
    """

    mhouseNm = serializers.CharField(source="name")
    buildYear = serializers.IntegerField(source="build_year")
    sggCd = serializers.CharField(source="regional_code")
    jibun = serializers.CharField(source="lot_number")
    road_name_address = serializers.CharField(allow_null=True, allow_blank=True)
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
            "mhouseNm",
            "buildYear",
            "sggCd",
            "jibun",
            "road_name_address",
            "address",
            "real_estate_type",
            "latitude",
            "longitude",
            "point",
        )

    def get_organized_data(self, deal_price_of_real_estates):
        real_estate_result = []
        deal_result = []

        for (
            _,
            deal_price_of_real_estate,
        ) in deal_price_of_real_estates.iterrows():
            deal_result.append(deal_price_of_real_estate)

            if self._already_exist_then_skip(deal_price_of_real_estate):
                continue

            deal_price_of_real_estate = dict(deal_price_of_real_estate)

            # self._set_name(deal_price_of_real_estate)

            is_set = self._set_address(deal_price_of_real_estate)
            if not is_set:
                continue

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

            real_estate_result.append(deal_price_of_real_estate)
        return real_estate_result, deal_result

    def _already_exist_then_skip(self, deal_price_of_real_estate):
        unique_key = f"{deal_price_of_real_estate.get(RealEstateKeyEnum.지역코드.value)}{deal_price_of_real_estate.get(RealEstateKeyEnum.지번.value)}"
        unique_keys = self.context.get("unique_keys")
        if unique_key in unique_keys:
            return True
        unique_keys[unique_key] = None
        return False

    def _set_address(self, deal_price_of_real_estate):
        dong = deal_price_of_real_estate.get(RealEstateKeyEnum.법정동.value)
        lot_number = deal_price_of_real_estate.get(RealEstateKeyEnum.지번.value)
        query = f"{dong} {lot_number}"
        address_converter_util = self.context.get("address_converter_util")
        if not address_converter_util.convert_address(query=query):
            file_logger.info(
                f"address_converter_util failed 주소 정보가 없음 query : {query}"
            )
            return False

        address_info = address_converter_util.get_address()
        deal_price_of_real_estate["address_info"] = address_info
        return True


class DealSerializer(serializers.ModelSerializer):
    dealAmount = serializers.IntegerField(source="deal_price")
    dealingGbn = serializers.CharField(source="brokerage_type")
    dealYear = serializers.IntegerField(source="deal_year")
    landAr = serializers.CharField(source="land_area")
    dealMonth = serializers.IntegerField(source="deal_month")
    dealDay = serializers.IntegerField(source="deal_day")
    excluUseAr = serializers.CharField(source="area_for_exclusive_use")
    cdealType = serializers.BooleanField(source="is_deal_canceled")
    cdealDay = serializers.DateField(
        source="deal_canceled_date", allow_null=True
    )
    real_estate_id = serializers.IntegerField()

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.pyung = None
        self.area_for_exclusive_use_pyung = None

    class Meta:
        model = Deal
        fields = (
            "id",
            "dealAmount",
            "dealingGbn",
            "dealYear",
            "landAr",
            "dealMonth",
            "dealDay",
            "excluUseAr",
            "floor",
            "cdealType",
            "cdealDay",
            "area_for_exclusive_use_pyung",
            "area_for_exclusive_use_price_per_pyung",
            "deal_type",
            "real_estate_id",
        )

    def get_organized_data(
        self, inserted_real_estate_models_dict, deal_price_of_real_estate_list
    ):
        for deal_price_of_real_estate in deal_price_of_real_estate_list:
            deal_price_of_real_estate[RealEstateKeyEnum.거래유형.value] = (
                BrokerageTypesEnum.BROKERAGE.value
                if deal_price_of_real_estate[RealEstateKeyEnum.거래유형.value]
                == "중개거래"
                else BrokerageTypesEnum.DIRECT.value
            )
            deal_price_of_real_estate["deal_type"] = (
                DealTypesForDBEnum.DEAL.value
            )

            self.cast_price_to_int(deal_price_of_real_estate)

            self.convert_square_meter_to_pyung(deal_price_of_real_estate)

            self.calc_price_per_pyung(deal_price_of_real_estate)

            self.set_is_deal_canceled(deal_price_of_real_estate)

            self.stringify_floor(deal_price_of_real_estate)

            self.set_deal_type(deal_price_of_real_estate)

            if inserted_real_estate_models_dict:
                self.set_real_estate_id(
                    deal_price_of_real_estate, inserted_real_estate_models_dict
                )

    def cast_price_to_int(self, instance):
        instance[RealEstateKeyEnum.거래금액.value] = int(
            instance[RealEstateKeyEnum.거래금액.value].replace(",", "")
        )

    def convert_square_meter_to_pyung(self, instance):
        area = instance[RealEstateKeyEnum.전용면적.value]

        self.pyung = round(Decimal(area) / Decimal(3.305785), 2)
        instance["area_for_exclusive_use_pyung"] = str(self.pyung)

    def calc_price_per_pyung(self, instance):
        price = instance[RealEstateKeyEnum.거래금액.value]
        instance["area_for_exclusive_use_price_per_pyung"] = str(
            round(price / self.pyung, 2)
        )

    @staticmethod
    def set_is_deal_canceled(instance):
        instance[RealEstateKeyEnum.해제여부.value] = (
            instance[RealEstateKeyEnum.해제여부.value] == "O"
        )

    def stringify_floor(self, instance):
        instance[RealEstateKeyEnum.층.value] = str(
            instance[RealEstateKeyEnum.층.value]
        )

    def set_deal_type(self, instance):
        instance[RealEstateKeyEnum.거래유형.value] = instance["deal_type"]

    def set_real_estate_id(self, instance, inserted_real_estate_models_dict):
        if not instance:
            file_logger.error("instance 없음")
        unique_key = f"{instance[RealEstateKeyEnum.지역코드.value]}{instance[RealEstateKeyEnum.지번.value]}"
        real_estate = inserted_real_estate_models_dict[unique_key]
        instance["real_estate_id"] = real_estate.id


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

    area_for_exclusive_use = serializers.CharField(max_length=10)
    area_for_exclusive_use_pyung = serializers.CharField(max_length=7)
    area_for_exclusive_use_price_per_pyung = serializers.CharField(max_length=8)


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


class RegionPriceSerializer(serializers.Serializer):
    region_id = serializers.IntegerField()
    total_deal_price = serializers.IntegerField(allow_null=True)
    total_jeonse_price = serializers.IntegerField(allow_null=True)
    total_deal_price_per_pyung = serializers.CharField(
        max_length=15, allow_null=True
    )
    total_jeonse_price_per_pyung = serializers.CharField(
        max_length=15, allow_null=True
    )
    average_deal_price = serializers.CharField(max_length=15, allow_null=True)
    average_jeonse_price = serializers.CharField(max_length=15, allow_null=True)
    average_deal_price_per_pyung = serializers.CharField(
        max_length=15, allow_null=True
    )
    average_jeonse_price_per_pyung = serializers.CharField(
        max_length=15, allow_null=True
    )
    deal_date = serializers.DateField()
    deal_count = serializers.IntegerField()
    jeonse_count = serializers.IntegerField()

    def create(self, validated_data):
        return RegionPrice.objects.create(**validated_data)


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
