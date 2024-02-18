from django.urls import reverse
import pytest


@pytest.mark.django_db(transaction=True)
def test_signup_view(client):
    url = reverse("signup")

    data = {"username": "test1", "password": "1234"}

    response = client.post(path=url, data=data)

    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_login_view(client, create_user):
    create_user(username="test1", password="1234")
    url = reverse("login")

    data = {"username": "test1", "password": "1234"}

    response = client.post(path=url, data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
