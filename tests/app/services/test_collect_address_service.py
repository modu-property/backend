import pytest
from real_estate.services.collect_region_service import CollectRegionService


@pytest.mark.django_db
class TestCollectRegionService:
    def test_collect_address(self, mocker, get_dongs):
        dongs_df = get_dongs(count=5)
        mocker.patch(
            "PublicDataReader.code_bdong",
            return_value=dongs_df,
        )

        result: bool = CollectRegionService().collect_region()

        for region in result:
            assert region.latitude is not None
            assert region.longitude is not None
