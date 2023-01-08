import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_news_when_news_exist_then_success(client, create_news):
    # given
    url = reverse("get_news")

    # when
    response = client.get(url)

    # then
    assert response.status_code == 200
    result = response.json()[0]
    assert result["id"] == create_news.id
    assert result["title"] == create_news.title


@pytest.mark.django_db
def test_get_news_when_news_not_exist_then_404(
    client,
):
    # given
    url = reverse("get_news")

    # when
    response = client.get(url)

    # then
    assert response.status_code == 404
