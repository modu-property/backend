import pytest
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_address_service import CollectRegionService


@pytest.mark.django_db
class TestCollectRegionService:
    def test_collect_address(self, mocker, get_dongs):
        dongs_df = get_dongs(count=5)
        mocker.patch(
            "PublicDataReader.code_bdong",
            return_value=dongs_df,
        )

        result: bool = CollectRegionService().collect_region()

        assert result == True

        regions = RealEstateRepository().get_regions()
        for region in regions:
            assert region.latitude is not None
            assert region.longitude is not None
