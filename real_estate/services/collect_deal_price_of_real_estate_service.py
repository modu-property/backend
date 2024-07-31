from dependency_injector.wiring import Provide, inject
from pandas import DataFrame

from modu_property.utils.loggers import logger, file_logger
from real_estate.containers.utils.address_converter_container import (
    AddressConverterContainer,
)
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.deal_enum import DealTypesForQueryEnum, DealTypesForDBEnum
from real_estate.enum.real_estate_enum import (
    RealEstateTypesForDBEnum,
    RealEstateTypesForQueryEnum,
    RealEstateKeyEnum,
)

from real_estate.models import Deal, RealEstate
from real_estate.serializers import DealSerializer, RealEstateSerializer
from real_estate.utils.address_converter_util import KakaoAddressConverterUtil
from real_estate.utils.real_estate_collector_util import RealEstateCollectorUtil
from real_estate.containers.utils.real_estate_collector_container import (
    RealEstateCollectorContainer,
)

"""
일단 한 클래스에서 수집하고 나중에 필요하면 아파트, 빌라별로 클래스 생성
"""


class CollectDealPriceOfRealEstateService:
    @inject
    def __init__(
        self,
        real_estate_collector: RealEstateCollectorUtil = Provide[
            RealEstateCollectorContainer.real_estate_collector
        ],
        address_converter_util: KakaoAddressConverterUtil = Provide[
            AddressConverterContainer.address_converter
        ],
    ) -> None:
        self.real_estate_collector: RealEstateCollectorUtil = (
            real_estate_collector
        )
        self.address_converter_util: KakaoAddressConverterUtil = (
            address_converter_util
        )
        self.delete = Delete()
        self.create_real_estate = CreateRealEstate(
            address_converter_util=self.address_converter_util
        )
        self.create_deal = CreateDeal()

    def collect_deal_price_of_real_estate(
        self, dto: CollectDealPriceOfRealEstateDto
    ):
        deal_prices_of_real_estate: DataFrame = (
            self.real_estate_collector.collect_deal_price_of_real_estate(
                dto=dto
            )
        )

        if (
            deal_prices_of_real_estate is False
            or deal_prices_of_real_estate.empty
        ):
            return

        deal_prices_of_real_estate = self.delete.delete_duplication(
            dto, deal_prices_of_real_estate
        )

        if deal_prices_of_real_estate.empty:
            return

        result = self.create_real_estate.create_real_estates(
            deal_prices_of_real_estate=deal_prices_of_real_estate, dto=dto
        )

        if not result:
            return

        return self.create_deal.create_deals(result)


class CreateRealEstate:
    def __init__(self, address_converter_util: KakaoAddressConverterUtil):
        self.address_converter_util = address_converter_util

    def create_real_estates(
        self,
        deal_prices_of_real_estate: DataFrame,
        dto: CollectDealPriceOfRealEstateDto,
    ):
        unique_keys = {}

        real_estate_type = self.convert_real_estate_type(dto)
        if not real_estate_type:
            logger.error(
                f"right real_estate_type not exist : {real_estate_type}"
            )
            return False

        serializer = RealEstateSerializer(
            context={
                "address_converter_util": self.address_converter_util,
                "real_estate_type": real_estate_type,
                "unique_keys": unique_keys,
            },
        )

        deal_price_of_real_estates = serializer.get_organized_data(
            deal_price_of_real_estates=deal_prices_of_real_estate
        )

        serializer = RealEstateSerializer(
            data=deal_price_of_real_estates, many=True
        )
        serializer.is_valid(raise_exception=True)

        real_estate_models = [
            RealEstate(**data) for data in serializer.validated_data
        ]

        inserted_real_estate_models = []
        try:
            if real_estate_models:
                inserted_real_estate_models = RealEstate.objects.bulk_create(
                    real_estate_models
                )
            return inserted_real_estate_models, deal_price_of_real_estates
        except Exception as e:
            logger.error(
                f"real_estate bulk_create e : {e} inserted_real_estate_models : {inserted_real_estate_models}"
            )
            return False

    @staticmethod
    def convert_real_estate_type(dto: CollectDealPriceOfRealEstateDto) -> str:
        if (
            dto.real_estate_type
            == RealEstateTypesForQueryEnum.MULTI_UNIT_HOUSE.value
        ):
            return RealEstateTypesForDBEnum.MULTI_UNIT_HOUSE.value
        return ""


class CreateDeal:
    def create_deals(self, result):
        (
            inserted_real_estate_models,
            deal_price_of_real_estate_list,
        ) = result
        inserted_real_estate_models_dict = (
            self.create_inserted_real_estate_models_dict(
                inserted_real_estate_models
            )
        )

        serializer = DealSerializer()
        serializer.get_organized_data(
            inserted_real_estate_models_dict, deal_price_of_real_estate_list
        )
        serializer = DealSerializer(
            data=deal_price_of_real_estate_list, many=True
        )
        serializer.is_valid(raise_exception=True)

        deal_models = [Deal(**data) for data in serializer.validated_data]

        try:
            if deal_models:
                Deal.objects.bulk_create(deal_models)
            return True
        except Exception as e:
            logger.error(f"deal bulk_create e : {e}")
        return False

    @staticmethod
    def create_inserted_real_estate_models_dict(inserted_real_estate_models):
        inserted_real_estate_models_dict = {}
        for inserted_real_estate_model in inserted_real_estate_models:
            regional_code = inserted_real_estate_model.regional_code
            lot_number = inserted_real_estate_model.lot_number
            unique_key = f"{regional_code}{lot_number}"
            inserted_real_estate_models_dict[unique_key] = (
                inserted_real_estate_model
            )
        return inserted_real_estate_models_dict


class Delete:
    def delete_duplication(
        self, dto: CollectDealPriceOfRealEstateDto, deal_prices_of_real_estate
    ):
        file_logger.info("delete_duplication")
        unique_keys_in_db = self.create_unique_keys_in_db(dto=dto)

        indexes_to_drop = self.create_indexes_to_drop(
            deal_prices_of_real_estate, unique_keys_in_db
        )

        deal_prices_of_real_estate = deal_prices_of_real_estate.drop(
            indexes_to_drop
        )

        return deal_prices_of_real_estate

    @staticmethod
    def create_indexes_to_drop(deal_prices_of_real_estate, unique_keys_in_db):
        indexes_to_drop = []
        for (
            index,
            deal_price_of_real_estate,
        ) in deal_prices_of_real_estate.iterrows():
            regional_code = deal_price_of_real_estate[
                RealEstateKeyEnum.지역코드.value
            ]
            lot_number = deal_price_of_real_estate[RealEstateKeyEnum.지번.value]
            unique_key = f"{regional_code}{lot_number}"

            if unique_key in unique_keys_in_db:
                indexes_to_drop.append(deal_prices_of_real_estate.index[index])
        return indexes_to_drop

    def create_unique_keys_in_db(self, dto: CollectDealPriceOfRealEstateDto):
        unique_keys_in_db = {}
        data_in_db = self.get_data_in_db(dto)
        for data in data_in_db:
            regional_code = data.regional_code
            lot_number = data.lot_number
            unique_key = f"{regional_code}{lot_number}"

            unique_keys_in_db[unique_key] = True
        return unique_keys_in_db

    @staticmethod
    def get_data_in_db(dto: CollectDealPriceOfRealEstateDto):
        _deal_type = (
            DealTypesForDBEnum.DEAL.value
            if dto.deal_type == DealTypesForQueryEnum.DEAL.value
            else None
        )

        return list(
            RealEstate.objects.prefetch_related("deals")
            .filter(
                regional_code=dto.regional_code,
                deals__deal_year=int(dto.year_month[:4]),
                deals__deal_month=int(dto.year_month[4:]),
                deals__deal_type=_deal_type,
            )
            .all()
        )
