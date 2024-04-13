from abc import ABC, abstractmethod
from typing import List, OrderedDict, Union
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnMapDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.repository.real_estate_repository import RealEstateRepository
from django.db.models import QuerySet

from real_estate.serializers import (
    GetRealEstatesOnMapResponseSerializer,
    GetRegionsOnMapResponseSerializer,
)


class GetRealEstatesInterface(ABC):
    @abstractmethod
    def get_real_estates(
        self, dto: GetRealEstatesOnMapDto
    ) -> Union[List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool]:
        pass


class GetRealEstates(GetRealEstatesInterface):
    def __init__(self, repository: RealEstateRepository) -> None:
        self.repository = repository

    def get_real_estates(
        self, dto: GetRealEstatesOnMapDto
    ) -> Union[List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool]:
        real_estates: Union[QuerySet, bool] = (
            self.repository.get_individual_real_estates(dto=dto)
        )

        if not real_estates:
            return ServiceResultDto(
                status_code=404,
            )

        data: Union[List[OrderedDict[str, Union[int, str]]], bool] = validate_data(
            queryset=real_estates,
            serializer=GetRealEstatesOnMapResponseSerializer,
            many=True,
        )

        if data:
            return ServiceResultDto(data=data)

        return ServiceResultDto(
            message="GetRealEstatesOnMapResponseSerializer 에러",
            status_code=400,
        )


class GetRegions(GetRealEstatesInterface):
    def __init__(self, repository: RealEstateRepository) -> None:
        self.repository = repository

    def get_real_estates(
        self, dto: GetRealEstatesOnMapDto
    ) -> Union[List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool]:
        regions: Union[QuerySet, bool] = self.repository.get_region_prices(dto=dto)

        if not regions:
            return ServiceResultDto(
                status_code=404,
            )

        data: Union[List[OrderedDict[str, Union[int, str]]], bool] = validate_data(
            queryset=regions,
            serializer=GetRegionsOnMapResponseSerializer,
            many=True,
        )

        if data:
            return ServiceResultDto(data=data)

        return ServiceResultDto(
            message="GetRegionsOnMapResponseSerializer 에러",
            status_code=400,
        )
