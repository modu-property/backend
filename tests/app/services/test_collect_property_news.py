import pytest

from app.services.collect_property_news import CollectPropertyNewsService


@pytest.mark.django_db
def test_collect_property_news_service(client):
    service = CollectPropertyNewsService()
    service.execute()
