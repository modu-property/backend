from dependency_injector.wiring import Provide

from modu_property.utils.loggers import logger
from real_estate.containers.repository_container import RepositoryContainer
from modu_property.utils.time import TimeUtil
from real_estate.management.commands.collect_command_mixin import (
    CollectCommandMixin,
)
from real_estate.repository.real_estate_repository import RealEstateRepository
from real_estate.services.collect_region_price_service import (
    CollectRegionPriceService,
)
from django.core.management.base import BaseCommand

from real_estate.utils.get_collecting_period_util import GetCollectingPeriodUtil


class Command(BaseCommand, CollectCommandMixin):
    help = "지역 단위 매매, 전세 가격 정보 수집하는 명령어"

    def __init__(
        self,
        repository: RealEstateRepository = Provide[
            RepositoryContainer.repository
        ],
    ):
        super(BaseCommand, self).__init__()
        super(CollectCommandMixin, self).__init__()

        self.service = CollectRegionPriceService()
        self.repository: RealEstateRepository = repository

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

        self.service.execute(sido, start_date, end_date)
