import logging
import os
from django.forms import model_to_dict
from django.contrib.gis.geos import Point
from modu_property.utils.validator import validate_model

from real_estate.models import Deal, RealEstate
from real_estate.serializers import DealSerializer, RealEstateSerializer
from real_estate.utils.address_getter import AddressGetter
from real_estate.utils.real_estate_collector import RealEstateCollector

"""
일단 한 클래스에서 수집하고 나중에 필요하면 아파트, 빌라별로 클래스 생성
"""

logger = logging.getLogger("django")


class CollectDealPriceOfRealEstateService:
    def __init__(self, url: str, type: str) -> None:
        self.url = url
        self.type = type
        self.service_key = os.getenv("SERVICE_KEY")

        self.real_estate_collector = RealEstateCollector()
        self.address_getter = AddressGetter()

    def execute(self, dong_code, deal_ymd):
        params = {
            "serviceKey": self.service_key,
            "LAWD_CD": dong_code,
            "DEAL_YMD": deal_ymd,
        }
        deal_prices_of_real_estate = (
            self.real_estate_collector.collect_deal_price_of_real_estate(
                url=self.url, params=params
            )
        )

        if not deal_prices_of_real_estate:
            return

        real_estate_models = []
        deal_models = []
        for deal_price_of_real_estate in deal_prices_of_real_estate:
            validated_real_estate = self.create_validated_real_estate(
                deal_price_of_real_estate
            )
            if not validated_real_estate:
                logger.error(
                    f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                )
                return False

            real_estate_models.append(RealEstate(**validated_real_estate))

            inserted_real_estate_models = []
            try:
                if real_estate_models:
                    inserted_real_estate_models = RealEstate.objects.bulk_create(
                        real_estate_models
                    )
            except Exception as e:
                logger.error(f"real_estate bulk_create params : {params}, e : {e}")
                return False

            for inserted_real_estate_model in inserted_real_estate_models:
                validated_deal = self.create_validated_deal_model(
                    deal_price_of_real_estate, inserted_real_estate_model
                )
                if not validated_deal:
                    logger.error(
                        f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                    )
                    return False

                deal_models.append(Deal(**validated_deal))

            try:
                if deal_models:
                    Deal.objects.bulk_create(deal_models)
                    return True
            except Exception as e:
                logger.error(f"deal bulk_create params : {params}, e : {e}")
                return False

    def create_validated_deal_model(
        self, deal_price_of_real_estate, inserted_real_estate_model
    ):
        deal_model = self.create_deal_model(
            deal_price_of_real_estate, inserted_real_estate_model
        )

        deal_dict = model_to_dict(deal_model)

        validated_deal_model = validate_model(
            model=deal_model,
            data=deal_dict,
            serializer=DealSerializer,
        )

        return validated_deal_model

    def create_validated_real_estate(self, deal_price_of_real_estate):
        address_info = self.address_getter.get_address_info(
            dong=deal_price_of_real_estate["법정동"],
            lot_number=deal_price_of_real_estate["지번"],
        )

        real_estate_model = self.create_real_estate_model(
            deal_price_of_real_estate, address_info
        )

        real_estate_dict = model_to_dict(real_estate_model)

        validated_real_estate_model = validate_model(
            model=real_estate_model,
            data=real_estate_dict,
            serializer=RealEstateSerializer,
        )

        return validated_real_estate_model

    def create_deal_model(
        self, deal_price_of_real_estate, inserted_real_estate_model
    ) -> Deal:
        return Deal(
            deal_price=deal_price_of_real_estate["거래금액"],
            deal_type=deal_price_of_real_estate["거래유형"],
            deal_year=deal_price_of_real_estate["년"],
            land_area=deal_price_of_real_estate["대지권면적"],
            deal_month=deal_price_of_real_estate["월"],
            deal_day=deal_price_of_real_estate["일"],
            area_for_exclusive_use=deal_price_of_real_estate["전용면적"],
            floor=deal_price_of_real_estate["층"],
            is_deal_canceled=deal_price_of_real_estate["해제여부"],
            deal_canceled_date=deal_price_of_real_estate["해제사유발생일"],
            type=self.type,
            real_estate_id=inserted_real_estate_model.id,
        )

    def create_real_estate_model(
        self, deal_price_of_real_estate, address_info
    ) -> RealEstate:
        return RealEstate(
            name=deal_price_of_real_estate["연립다세대"],
            build_year=deal_price_of_real_estate["건축년도"],
            regional_code=deal_price_of_real_estate["지역코드"],
            lot_number=deal_price_of_real_estate["지번"],
            road_name_address=address_info["road_name_address"],
            latitude=address_info["latitude"],
            longitude=address_info["longitude"],
            point=Point(
                float(address_info["latitude"]), float(address_info["longitude"])
            ),
        )
