from typing import Union

from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import User


@api_view(("POST",))
def login(request: Request) -> Union[Response, HttpResponseRedirect]:
    body = request.POST
    username = body["username"]
    password = body["password"]

    user = User.objects.get(username=username)
    is_authenticated = check_password(password, user.password)

    if is_authenticated:
        data = {
            "username": username,
            "password": password,
        }
        url = request.build_absolute_uri(reverse("token_obtain_pair"))
        response = requests.post(url, data=data)
        if response.status_code != 200:
            return Response("로그인 실패", 401)

        return Response(data=response.json())


@api_view(("POST",))
def signup(request: Request) -> Response:
    body = request.POST
    username = body["username"]
    password = body["password"]

    encrypted_password = make_password(password)
    user = User(username=username, password=encrypted_password)
    user.save()

    return Response("회원가입 성공")
