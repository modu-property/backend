from real_estate.utils.address_collector import AddressCollector


class CollectAddressService:
    def __init__(
        self,
    ) -> None:
        self.address_collector = AddressCollector()

    def execute(self):
        return self.address_collector.collect_regional_info()
