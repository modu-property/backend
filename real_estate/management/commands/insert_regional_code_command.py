from django.core.management.base import BaseCommand
from modu_property.utils.loggers import logger

from real_estate.services.insert_address_service import InsertAddressService


class Command(BaseCommand):
    help = ".sql 지역 코드 파일 실행하는 명령어"

    def __init__(self):
        self.service = InsertAddressService()

    def handle(self, *args, **options):
        result = self.service.execute()

        logger.info(f"result : {result}")
