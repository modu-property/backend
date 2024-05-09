import pytest
from django.urls import reverse


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
    url = reverse("get-real-estates-on-search", kwargs={"deal_type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {
        "keyword": "강남",
    }

    response = client.get(url, data=query_params, **headers)
    assert response.status_code == 200
