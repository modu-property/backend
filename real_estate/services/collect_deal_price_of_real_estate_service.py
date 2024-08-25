from typing import Tuple

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
from real_estate.repository.real_estate_repository import RealEstateRepository
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
        self.segregator = Segregator()
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
        file_logger.debug(
            f"deal_prices_of_real_estate : {deal_prices_of_real_estate}"
        )

        if (
            deal_prices_of_real_estate is False
            or deal_prices_of_real_estate.empty
        ):
            return

        """
        DB에 이미 있는 real_estate면 create real_estate 생략
        이미 있으면 real_estate id랑 deal 따로 구하기, 나머지는 그대로 로직 타기
        """

        deal_prices_about_new_real_estate, deal_prices_about_new_deal = (
            self.segregator.segregate_real_estates(
                dto, deal_prices_of_real_estate
            )
        )

        if not deal_prices_about_new_real_estate.empty:
            result = self._create_new_real_estates_and_new_deals(
                dto, deal_prices_about_new_real_estate
            )

            if not result:
                return

        if not deal_prices_about_new_deal.empty:
            self.create_deal.create_only_new_deals(deal_prices_about_new_deal)

        return True

    def _create_new_real_estates_and_new_deals(
        self, dto, deal_prices_about_new_real_estate
    ):
        result = self.create_real_estate.create_real_estates(
            deal_prices_of_real_estate=deal_prices_about_new_real_estate,
            dto=dto,
        )

        if not result:
            return

        self.create_deal.create_deals(result)

        return True


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

        deal_price_of_real_estates, deal_result = serializer.get_organized_data(
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
            return (
                inserted_real_estate_models,
                deal_result,
            )
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
    def __init__(self):
        self.repository = RealEstateRepository()

    def create_only_new_deals(self, deal_prices_about_new_deal: DataFrame):
        serializer = DealSerializer()
        deal_dict_list = []

        for _, deal in deal_prices_about_new_deal.iterrows():
            deal_dict_list.append(dict(deal))

        serializer.get_organized_data(None, deal_dict_list)

        serializer = DealSerializer(data=deal_dict_list, many=True)
        serializer.is_valid(raise_exception=True)

        deal_models = [Deal(**data) for data in serializer.validated_data]

        try:
            if deal_models:
                Deal.objects.bulk_create(deal_models)
            return True
        except Exception as e:
            logger.error(f"deal bulk_create e : {e}")
        return False

    def create_deals(self, result):
        (
            inserted_real_estate_models,
            deal_result,
        ) = result
        inserted_real_estate_models_dict = (
            self.create_inserted_real_estate_models_dict(
                inserted_real_estate_models
            )
        )

        serializer = DealSerializer()

        deal_prices_of_real_estate = [deal.to_dict() for deal in deal_result]

        serializer.get_organized_data(
            inserted_real_estate_models_dict, deal_prices_of_real_estate
        )
        serializer = DealSerializer(data=deal_prices_of_real_estate, many=True)
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


class Segregator:
    def __init__(self):
        self.repository = RealEstateRepository()

    def segregate_real_estates(
        self, dto: CollectDealPriceOfRealEstateDto, deal_prices_of_real_estate
    ):
        """
        DB에 있는 real_estates와 DB에 없는 새로운 real_estates를 반환함
        """

        file_logger.info("segregate_real_estates")
        unique_keys_in_db = self.create_unique_keys_in_db(dto=dto)

        return self.get_new_real_estates_and_deals(
            deal_prices_of_real_estate, unique_keys_in_db
        )

    def get_new_real_estates_and_deals(
        self, deal_prices_of_real_estate, unique_keys_in_db
    ) -> Tuple[DataFrame, DataFrame]:
        new_real_estates = []
        deals = []

        """
        deal_prices_of_real_estate에 unique_keys_in_db랑 일치하는 게 있으면  deals에 저장, 나머지는 new_real_estates에 저장 
        """
        for (
            _,
            deal_price_of_real_estate,
        ) in deal_prices_of_real_estate.iterrows():
            regional_code = deal_price_of_real_estate[
                RealEstateKeyEnum.지역코드.value
            ]
            lot_number = deal_price_of_real_estate[RealEstateKeyEnum.지번.value]
            unique_key = f"{regional_code}{lot_number}"

            if unique_key in unique_keys_in_db:
                deal_price_of_real_estate["real_estate_id"] = unique_keys_in_db[
                    unique_key
                ]
                deals.append(deal_price_of_real_estate)
            else:
                new_real_estates.append(deal_price_of_real_estate)

        return DataFrame(new_real_estates), DataFrame(deals)

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
        data_in_db = self.repository.get_real_estates_on_this_month(dto)
        for data in data_in_db:
            regional_code = data.regional_code
            lot_number = data.lot_number
            unique_key = f"{regional_code}{lot_number}"

            unique_keys_in_db[unique_key] = data.id
        return unique_keys_in_db
