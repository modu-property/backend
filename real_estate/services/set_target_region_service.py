from real_estate.dto.collect_region_price_dto import CollectRegionPriceDto


class SetTargetRegionService:
    @classmethod
    def set_target_region(cls, dto: CollectRegionPriceDto):
        if dto.region.sido:
            cls._filter_sido(dto=dto)
        if dto.region.dongri:
            dto.target_region = f"{dto.region.sido} {dto.region.sigungu} {dto.region.ubmyundong} {dto.region.dongri}"
        elif dto.region.ubmyundong:
            dto.target_region = f"{dto.region.sido} {dto.region.sigungu} {dto.region.ubmyundong}"
        elif dto.region.sigungu:
            dto.target_region = f"{dto.region.sido} {dto.region.sigungu}"
        elif dto.region.sido:
            dto.target_region = dto.region.sido

    @classmethod
    def _filter_sido(cls, dto: CollectRegionPriceDto):
        sido: str = dto.region.sido
        if "특별시" in sido:
            dto.region.sido = "서울"
        elif "광역시" in sido:
            dto.region.sido = sido[2:]
        elif "남도" in sido or "북도" in sido:
            dto.region.sido = sido[0] + sido[2]
        elif "경기도" in sido:
            dto.region.sido = "경기"
        elif "특별" in sido:
            pass
