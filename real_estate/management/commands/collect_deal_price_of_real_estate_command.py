import threading
from django.core.management.base import BaseCommand
from manticore.manticore_client import ManticoreClient
from real_estate.dto.collect_address_dto import CollectDealPriceOfRealEstateDto
from real_estate.enum.real_estate_enum import RealEstateTypesForQueryEnum
from real_estate.enum.deal_enum import DealTypesForQueryEnum
from real_estate.management.commands.collect_command_mixin import CollectCommandMixin
from modu_property.utils.time import TimeUtil
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_deal_price_of_real_estate_service import (
    CollectDealPriceOfRealEstateService,
)


class Command(BaseCommand, CollectCommandMixin):
    help = "매매, 전월세 내역 수집하는 명령어"

    def __init__(self):
        super(BaseCommand, self).__init__()
        super(CollectCommandMixin, self).__init__()

        self.service = CollectDealPriceOfRealEstateService()
        self.deal_types: list[str] = DealTypesForQueryEnum.get_deal_types()
        self.real_estate_types: list[str] = (
            RealEstateTypesForQueryEnum.get_real_estate_types()
        )
        self.repository = RealEstateRepository()

    @TimeUtil.timer
    def handle(self, *args, **options):
        sido, start_date, end_date = self.get_command_params(options)

        sejong_regional_code = "36110"

        regional_codes = []
        if sido:
            regions = self.repository.get_regions_exclude_branch(sido=sido)

            regional_codes = list(
                set([region.get("regional_code") for region in regions])
            )
        else:
            regional_codes.append(sejong_regional_code)

        years_and_months = None
        if not all([start_date, end_date]):
            last_deal = self.repository.get_last_deal()
            if not last_deal:
                raise Exception(
                    "시작/종료 연월과 deal 둘 다 없음. 둘 중에 하나는 있어야 함"
                )

            years_and_months = self.get_collecting_period(instance=last_deal)
        else:
            years_and_months = self.get_collecting_period(
                start_date=start_date, end_date=end_date
            )

        self.run_service(
            regional_codes=regional_codes, years_and_months=years_and_months
        )

    def run_service(self, regional_codes, years_and_months):
        for year_and_month in years_and_months:
            for real_estate_type in self.real_estate_types:
                for deal_type in self.deal_types:
                    threads = []
                    dto = None
                    for regional_code in regional_codes:
                        dto: CollectDealPriceOfRealEstateDto = (
                            CollectDealPriceOfRealEstateDto(
                                real_estate_type=real_estate_type,
                                year_month=year_and_month,
                                deal_type=deal_type,
                                regional_code=regional_code,
                            )
                        )
                        if self.not_test_env():
                            t = threading.Thread(
                                target=self.service.execute, args=(dto,)
                            )
                            t.start()
                            threads.append(t)
                        else:
                            self.service.execute(dto=dto)

                    if self.not_test_env():
                        for _thread in threads:
                            _thread.join()

                    manticore_client = ManticoreClient()
                    manticore_client.run_indexer()
