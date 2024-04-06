from django.core.management.base import BaseCommand
from modu_property.utils.loggers import logger

from real_estate.services.collect_address_service import CollectRegionService


class Command(BaseCommand):
    help = "지역 정보 수집하는 명령어"

    def __init__(self):
        self.service = CollectRegionService()

    def handle(self, *args, **options):
        result = self.service.collect()

        logger.error(f"result : {result}")
