import pytest

from app.models import News
from app.services.collect_property_news import CollectPropertyNewsService


@pytest.mark.django_db
def test_collect_property_news_service_with_mock(mock_search_news_by_naver_api):
    display = 1
    service = CollectPropertyNewsService(display=display)

    service.search_news_by_naver_api = mock_search_news_by_naver_api

    result = service.execute()
    assert result is True

    news = News.objects.all()
    assert len(news) != 0


@pytest.mark.skip("실제 뉴스 잘 가져오는지 테스트할 때 skip 주석처리하고 실행")
@pytest.mark.django_db
def test_collect_property_news_service():
    display = 5
    service = CollectPropertyNewsService(display=display)

    result = service.execute()
    assert result is True

    news = News.objects.all()
    assert len(news) > 0
