from django.urls import reverse

from tests.fixtures import *


@pytest.mark.django_db
def test_get_villas_with_latitude_longitude_zoom_level_view(
    client, get_jwt, create_villa
):
    url = reverse("villa", kwargs={"type": "deal"})

    _jwt = get_jwt

    headers = {"HTTP_AUTHORIZATION": f"Bearer {_jwt}"}
    query_params = {"latitude": 1, "longitude": 1, "zoom_level": 3, "keyword": ""}

    response = client.get(url, data=query_params, **headers)
    assert response.status_code == 200

    # post = Post.objects.get(id=1)
    # assert post.id == 1
    # assert post.title == data.get("title")


# @pytest.mark.django_db
# def test_create_post_view_when_invalid_request_then_400(client, get_jwt):
#     url = reverse("create_post")

#     _jwt = get_jwt

#     headers = {"HTTP_Authorization": _jwt}
#     data = {"title": "test_title", "content": ""}

#     response = client.post(path=url, **headers, data=data)
#     assert response.status_code == 400


# @pytest.mark.django_db
# def test_get_post_view(client, create_post):
#     url = reverse("get_post", kwargs={"id": 1})
#     response = client.get(url)
#     assert response.status_code == 200
#     assert response.data["title"] == "test_title"


# @pytest.mark.django_db
# def test_get_post_view_when_no_post_then_404(client):
#     url = reverse("get_post", kwargs={"id": 1})
#     response = client.get(url)
#     assert response.status_code == 404


# @pytest.mark.django_db
# def test_get_post_list(client, create_post):
#     url = reverse("get_post_list")
#     response = client.get(url)
#     assert response.status_code == 200


# @pytest.mark.django_db
# def test_get_post_list_when_no_post_then_404(client):
#     url = reverse("get_post_list")
#     response = client.get(url)
#     assert response.status_code == 404
