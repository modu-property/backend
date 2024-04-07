from abc import ABC, abstractmethod
from typing import List, OrderedDict, Union
from modu_property.utils.validator import validate_data
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnMapDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import RealEstateZoomLevel, RegionZoomLevel
from real_estate.repository.real_estate_repository import RealEstateRepository
from django.db.models import QuerySet

from real_estate.serializers import (
    GetRealEstatesOnMapResponseSerializer,
    GetRegionsOnMapResponseSerializer,
)


class GetProperty(ABC):
    @abstractmethod
    def get_property(
        self, dto: GetRealEstatesOnMapDto
    ) -> Union[List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool]:
        pass


class GetRealEstates(GetProperty):
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def get_property(
        self, dto: GetRealEstatesOnMapDto
    ) -> Union[List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool]:
        real_estates: Union[QuerySet, bool] = (
            self.repository.get_individual_real_estates(dto=dto)
        )

        if real_estates:
            data: Union[List[OrderedDict[str, Union[int, str]]], bool] = validate_data(
                queryset=real_estates,
                serializer=GetRealEstatesOnMapResponseSerializer,
                many=True,
            )

            if data:
                return ServiceResultDto(data=data)
            elif data is False:
                return ServiceResultDto(
                    message="GetRealEstatesOnMapResponseSerializer 에러",
                    status_code=400,
                )
        return ServiceResultDto(
            status_code=404,
        )


class GetRegions(GetProperty):
    def __init__(self) -> None:
        self.repository = RealEstateRepository()

    def get_property(
        self, dto: GetRealEstatesOnMapDto
    ) -> Union[List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool]:
        regions: Union[QuerySet, bool] = self.repository.get_region_prices(dto=dto)

        if regions:
            data: Union[List[OrderedDict[str, Union[int, str]]], bool] = validate_data(
                queryset=regions,
                serializer=GetRegionsOnMapResponseSerializer,
                many=True,
            )

            if data:
                return ServiceResultDto(data=data)
            elif data is False:
                return ServiceResultDto(
                    message="GetRegionsOnMapResponseSerializer 에러",
                    status_code=400,
                )
        return ServiceResultDto(
            status_code=404,
        )


class GetPropertiesOnMapService:
    def __init__(self) -> None:
        self.repository = RealEstateRepository()
        self.get_real_estates = GetRealEstates()
        self.get_regions = GetRegions()

    def get_properties(self, dto: GetRealEstatesOnMapDto) -> ServiceResultDto:
        if self._is_real_estates_zoom_level(dto=dto):
            real_estates: Union[
                List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
            ] = self.get_real_estates.get_property(dto=dto)

            if real_estates is None:
                return ServiceResultDto(status_code=404)

            return self._return_result(properties=real_estates)
        elif self._is_regions_zoom_level(dto=dto):
            regions: Union[
                List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
            ] = self.get_regions.get_property(dto=dto)

            if regions is None:
                return ServiceResultDto(status_code=404)

            return self._return_result(properties=regions)

        return ServiceResultDto(status_code=404)

    def _return_result(
        self,
        properties: Union[
            List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
        ],
    ) -> ServiceResultDto:
        if not properties:
            return ServiceResultDto(status_code=400)
        if isinstance(properties, ServiceResultDto):
            return properties
        return ServiceResultDto(data=properties)

    def _is_real_estates_zoom_level(self, dto):
        return (
            RealEstateZoomLevel.MIN.value <= dto.zoom_level
            and dto.zoom_level <= RealEstateZoomLevel.MAX.value
        )

    def _is_regions_zoom_level(self, dto):
        return (
            RegionZoomLevel.DONGRI.value <= dto.zoom_level
            and dto.zoom_level <= RegionZoomLevel.SIDO.value
        )
