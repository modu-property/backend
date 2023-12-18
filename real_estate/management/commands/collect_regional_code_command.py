from django.core.management.base import BaseCommand

from real_estate.services.collect_address_service import CollectAddressService


class Command(BaseCommand):
    help = "지역 코드 수집하는 명령어"

    def __init__(self):
        self.service = CollectAddressService()

    def handle(self, *args, **options):
        self.service.execute()
