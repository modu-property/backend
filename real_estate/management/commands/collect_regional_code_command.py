from dependency_injector.wiring import inject, Provide
from django.core.management.base import BaseCommand
from modu_property.utils.loggers import logger
from real_estate.containers.service_container import ServiceContainer

from real_estate.services.collect_address_service import CollectRegionService


class Command(BaseCommand):
    help = "지역 정보 수집하는 명령어"

    @inject
    def __init__(
        self,
        service: CollectRegionService = Provide[
            ServiceContainer.collect_regions_service
        ],
    ):
        self.service = service

    def handle(self, *args, **options):
        result = self.service.collect_region()

        logger.error(f"result : {result}")
