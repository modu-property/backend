from django.forms import model_to_dict
from django.contrib.gis.geos import Point
from pandas import DataFrame
from modu_property.utils.loggers import logger, file_logger
from modu_property.utils.validator import validate_data
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto

from real_estate.models import Deal, RealEstate
from real_estate.serializers import DealSerializer, RealEstateSerializer
from real_estate.utils.address_converter import AddressConverter
from real_estate.utils.real_estate_collector import RealEstateCollector

"""
일단 한 클래스에서 수집하고 나중에 필요하면 아파트, 빌라별로 클래스 생성
"""


class CollectDealPriceOfRealEstateService:
    def __init__(self) -> None:
        self.real_estate_collector = RealEstateCollector()
        self.address_converter = AddressConverter()

    def execute(self, dto: CollectDealPriceOfRealEstateDto):
        deal_prices_of_real_estate: DataFrame = (
            self.real_estate_collector.collect_deal_price_of_real_estate(dto=dto)
        )

        if deal_prices_of_real_estate is False or deal_prices_of_real_estate.empty:
            return

        deal_prices_of_real_estate = self.delete_duplication(
            dto, deal_prices_of_real_estate
        )

        if deal_prices_of_real_estate.empty:
            return

        result = self.create_real_estates(
            deal_prices_of_real_estate=deal_prices_of_real_estate
        )

        if not result:
            return

        (
            inserted_real_estate_models,
            deal_price_of_real_estate_list,
        ) = result

        inserted_real_estate_models_dict = self.get_inserted_real_estate_models_dict(
            inserted_real_estate_models
        )

        deal_models = self.get_deal_models(
            dto, deal_price_of_real_estate_list, inserted_real_estate_models_dict
        )

        try:
            if deal_models:
                Deal.objects.bulk_create(deal_models)
            return True
        except Exception as e:
            logger.error(f"deal bulk_create e : {e}")
        return False

    def delete_duplication(self, dto, deal_prices_of_real_estate):
        file_logger.info("delete_duplication")
        unique_keys_in_db = {}
        data_in_db = self.get_data_in_db(dto)
        for data in data_in_db:
            regional_code = data.regional_code
            lot_number = data.lot_number
            unique_key = f"{regional_code}{lot_number}"

            unique_keys_in_db[unique_key] = True

        indexes_to_drop = []
        for index, deal_price_of_real_estate in deal_prices_of_real_estate.iterrows():
            regional_code = deal_price_of_real_estate["지역코드"]
            lot_number = deal_price_of_real_estate["지번"]
            unique_key = f"{regional_code}{lot_number}"

            if unique_key in unique_keys_in_db:
                indexes_to_drop.append(deal_prices_of_real_estate.index[index])

        deal_prices_of_real_estate = deal_prices_of_real_estate.drop(indexes_to_drop)

        return deal_prices_of_real_estate

    def get_deal_models(
        self, dto, deal_price_of_real_estate_list, inserted_real_estate_models_dict
    ):
        deal_models = []
        for deal_price_of_real_estate in deal_price_of_real_estate_list:
            regional_code = deal_price_of_real_estate["지역코드"]
            lot_number = deal_price_of_real_estate["지번"]
            unique_key = f"{regional_code}{lot_number}"

            validated_deal = self.create_validated_deal_model(
                deal_price_of_real_estate,
                inserted_real_estate_models_dict[unique_key],
                dto.trade_type,
            )
            if not validated_deal:
                logger.error(
                    f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                )
                return False

            deal_models.append(Deal(**validated_deal))
        return deal_models

    def get_inserted_real_estate_models_dict(self, inserted_real_estate_models):
        inserted_real_estate_models_dict = {}
        for inserted_real_estate_model in inserted_real_estate_models:
            regional_code = inserted_real_estate_model.regional_code
            lot_number = inserted_real_estate_model.lot_number
            unique_key = f"{regional_code}{lot_number}"
            inserted_real_estate_models_dict[unique_key] = inserted_real_estate_model
        return inserted_real_estate_models_dict

    def create_real_estates(self, deal_prices_of_real_estate: DataFrame):
        deal_price_of_real_estate_list = []
        unique_keys = {}
        real_estate_models = []

        for _, deal_price_of_real_estate in deal_prices_of_real_estate.iterrows():
            regional_code = deal_price_of_real_estate["지역코드"]
            lot_number = deal_price_of_real_estate["지번"]
            unique_key = f"{regional_code}{lot_number}"

            validated_real_estate = self.create_validated_real_estate(
                deal_price_of_real_estate
            )
            if not validated_real_estate:
                logger.error(
                    f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                )
                return False

            if deal_price_of_real_estate.get("해제사유발생일"):
                canceled_date = deal_price_of_real_estate.get("해제사유발생일")
                y, m, d = canceled_date.split(".")
                y = f"20{y}"

                deal_price_of_real_estate["해제사유발생일"] = f"{y}-{m}-{d}"

            if not deal_price_of_real_estate.get("해제여부"):
                deal_price_of_real_estate["해제여부"] = False

            deal_price_of_real_estate_list.append(deal_price_of_real_estate)

            if unique_key not in unique_keys:
                real_estate_models.append(RealEstate(**validated_real_estate))
                unique_keys[unique_key] = ""

        try:
            inserted_real_estate_models = []
            if real_estate_models:
                inserted_real_estate_models = RealEstate.objects.bulk_create(
                    real_estate_models
                )
            return inserted_real_estate_models, deal_price_of_real_estate_list
        except Exception as e:
            logger.error(
                f"real_estate bulk_create e : {e} inserted_real_estate_models : {inserted_real_estate_models}"
            )
            return False

    def create_validated_deal_model(
        self, deal_price_of_real_estate, inserted_real_estate_model, type
    ):
        deal_model = self.create_deal_model(
            deal_price_of_real_estate, inserted_real_estate_model, type
        )

        deal_dict = model_to_dict(deal_model)

        validated_deal_model = validate_data(
            model=deal_model,
            data=deal_dict,
            serializer=DealSerializer,
        )

        return validated_deal_model

    def create_validated_real_estate(self, deal_price_of_real_estate):
        address_info = self.address_converter.convert_address(
            dong=deal_price_of_real_estate["법정동"],
            lot_number=deal_price_of_real_estate["지번"],
        )

        if not address_info:
            return False

        real_estate_model: RealEstate = self.create_real_estate_model(
            deal_price_of_real_estate=deal_price_of_real_estate,
            address_info=address_info,
        )

        real_estate_dict = model_to_dict(real_estate_model)

        validated_real_estate_model = validate_data(
            model=real_estate_model,
            data=real_estate_dict,
            serializer=RealEstateSerializer,
        )

        return validated_real_estate_model

    def create_deal_model(
        self, deal_price_of_real_estate, inserted_real_estate_model, type
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
            type=type,
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
            address=address_info["address"],
            latitude=address_info["latitude"],
            longitude=address_info["longitude"],
            point=Point(
                float(address_info["latitude"]), float(address_info["longitude"])
            ),
        )

    def get_data_in_db(self, dto):
        return list(
            RealEstate.objects.prefetch_related("deals")
            .filter(
                regional_code=dto.regional_code,
                deals__deal_year=int(dto.year_month[:4]),
                deals__deal_month=int(dto.year_month[4:]),
                deals__type=dto.trade_type,
                # deal__deal_type=None,
            )
            .all()
        )
