import pytest
from real_estate.services.collect_address_service import CollectAddressService


@pytest.mark.django_db
class TestCollectAddressService:
    def test_collect_address(self):
        result = CollectAddressService().execute()

        assert result == True
