import pytest
from django.urls import reverse
from rest_framework import status

from real_estate.enum.deal_enum import DealTypesForDBEnum


@pytest.mark.django_db(transaction=True, reset_sequences=True)
# @pytest.mark.skip()
def test_get_real_estates_with_keyword_view(client, get_jwt):
    """
    !!로컬 데이터 사라지므로 주의!!
    터미널에서 아래 명령어 실행
    SERVER_ENV=local python manage.py insert_real_estates_for_searching_command
    manticore container에서 indexing
    indexer --config /etc/manticoresearch/manticore.conf --all --rotate
    """
    url = reverse(
        "get-real-estates-on-search",
        kwargs={"deal_type": DealTypesForDBEnum.DEAL.value},
    )

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "keyword": "강남",
    }

    response = client.get(url, data=query_params, **headers)
    assert response.status_code == 200
    data = response.data
    assert "regions" in data
    assert "real_estates" in data
    assert data["regions"] != []
    assert data["real_estates"] != []


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_real_estates_with_keyword_view(client, get_jwt, mocker):
    mocker.patch(
        "real_estate.services.get_real_estates_on_search_service.GetRealEstatesOnSearchService._search_and_update_real_estates",
        return_value=False,
    )
    url = reverse(
        "get-real-estates-on-search",
        kwargs={"deal_type": DealTypesForDBEnum.DEAL.value},
    )

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "keyword": "강남",
    }

    response = client.get(url, data=query_params, **headers)
    response.status_code == status.HTTP_400_BAD_REQUEST
