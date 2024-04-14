from typing import List, OrderedDict, Union
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnMapDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import RealEstateZoomLevel, RegionZoomLevel

from dependency_injector.wiring import inject, Provide
from real_estate.containers.service_container import ServiceContainer
from real_estate.services.get_real_estates import (
    GetRealEstates,
    GetRegions,
)


class GetPropertiesOnMapService:
    @inject
    def __init__(
        self,
        get_real_estates: GetRealEstates = Provide[ServiceContainer.get_real_estates],
        get_regions: GetRegions = Provide[ServiceContainer.get_regions],
    ) -> None:
        self.get_real_estates = get_real_estates
        self.get_regions = get_regions

    def get_properties(self, dto: GetRealEstatesOnMapDto) -> ServiceResultDto:
        if self._is_real_estates_zoom_level(dto=dto):
            real_estates: Union[
                List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
            ] = self.get_real_estates.get_real_estates(dto=dto)

            if real_estates is None:
                return ServiceResultDto(status_code=404)

            return self._return_result(properties=real_estates)
        elif self._is_regions_zoom_level(dto=dto):
            regions: Union[
                List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
            ] = self.get_regions.get_real_estates(dto=dto)

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
