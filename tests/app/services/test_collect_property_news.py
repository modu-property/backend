import pytest

from app.models import News
from app.services.collect_property_news import CollectPropertyNewsService


@pytest.mark.django_db
def test_collect_property_news_service(mock_search_news_by_naver_api):
    display = 1
    service = CollectPropertyNewsService(display=display)

    service.search_news_by_naver_api = mock_search_news_by_naver_api

    result = service.execute()
    assert result is True

    news = News.objects.all()
    assert len(news) != 0
