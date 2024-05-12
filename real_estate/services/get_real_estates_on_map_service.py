from typing import List, OrderedDict, Union
from real_estate.dto.get_real_estate_dto import GetRealEstatesOnMapDto
from real_estate.dto.service_result_dto import ServiceResultDto
from real_estate.enum.real_estate_enum import (
    RealEstateZoomLevelEnum,
    RegionZoomLevelEnum,
)

from dependency_injector.wiring import inject, Provide
from real_estate.containers.service_container import ServiceContainer
from real_estate.services.get_real_estates_service import (
    GetRealEstatesService,
    GetRegionsService,
)


class GetRealEstatesOnMapService:
    @inject
    def __init__(
        self,
        get_real_estates: GetRealEstatesService = Provide[
            ServiceContainer.get_real_estates
        ],
        get_regions: GetRegionsService = Provide[ServiceContainer.get_regions],
    ) -> None:
        self.get_real_estates = get_real_estates
        self.get_regions = get_regions

    def get(self, dto: GetRealEstatesOnMapDto) -> ServiceResultDto:
        if self._is_real_estates_zoom_level(dto=dto):
            return self._get_real_estates(
                dto, method=self.get_real_estates.get_real_estates
            )
        elif self._is_regions_zoom_level(dto=dto):
            return self._get_real_estates(
                dto, method=self.get_regions.get_real_estates
            )
        return ServiceResultDto(status_code=404)

    def _get_real_estates(self, dto, method):
        real_estates: Union[
            List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
        ] = method(dto=dto)
        if real_estates is None:
            return ServiceResultDto(status_code=404)
        return self._return_result(properties=real_estates)

    @staticmethod
    def _return_result(
        properties: Union[
            List[OrderedDict[str, Union[int, str]]], ServiceResultDto, bool
        ],
    ) -> ServiceResultDto:
        if not properties:
            return ServiceResultDto(status_code=400)
        if isinstance(properties, ServiceResultDto):
            return properties
        return ServiceResultDto(data=properties)

    @staticmethod
    def _is_real_estates_zoom_level(dto):
        return (
            RealEstateZoomLevelEnum.MIN.value
            <= dto.zoom_level
            <= RealEstateZoomLevelEnum.MAX.value
        )

    @staticmethod
    def _is_regions_zoom_level(dto):
        return (
            RegionZoomLevelEnum.DONGRI.value
            <= dto.zoom_level
            <= RegionZoomLevelEnum.SIDO.value
        )
