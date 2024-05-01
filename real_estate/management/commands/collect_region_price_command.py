from modu_property.utils.time import TimeUtil
from django.core.management.base import BaseCommand

from real_estate.management.commands.collect_command_mixin import (
    CollectCommandMixin,
)
from real_estate.services.collect_region_price_service import (
    CollectRegionPriceService,
)


class Command(BaseCommand, CollectCommandMixin):
    help = "지역 단위 매매, 전세 가격 정보 수집하는 명령어"

    def __init__(
        self,
    ):
        super(BaseCommand, self).__init__()
        super(CollectCommandMixin, self).__init__()

        self.service = CollectRegionPriceService()

    def add_arguments(self, parser):
        parser.add_argument(
            "sido",
            type=str,
            help="서울특별시, 세종특별자치시, ...",
        )
        parser.add_argument(
            "start_date",
            type=str,
            help="200601",
        )
        parser.add_argument(
            "end_date",
            type=str,
            help="200612",
        )

    @TimeUtil.timer
    def handle(self, *args, **options):
        sido, start_date, end_date = self.get_command_params(options)

        self.service.collect_region_price_within_period(
            sido, start_date, end_date
        )
