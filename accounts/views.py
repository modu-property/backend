import os
import requests
from typing import Union
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseRedirect
from django.test import Client
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from accounts.models import User


@api_view(("POST",))
def signup(request: Request) -> Response:
    body = request.POST
    username = body["username"]
    password = body["password"]

    encrypted_password = make_password(password)
    user = User(username=username, password=encrypted_password)
    user.save()

    return Response("회원가입 성공")


@api_view(("POST",))
def login(request: Request) -> Union[Response, HttpResponseRedirect]:
    print(request)
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

        server_env = os.getenv("SERVER_ENV")
        url = request.build_absolute_uri(reverse("token_obtain_pair"))
        response = None
        if server_env == "test":
            client = Client()
            response = client.post(path=reverse("token_obtain_pair"), data=data)
        else:
            response = requests.post(path=url, data=data)

        if response.status_code != 200:
            return Response("로그인 실패", 401)

        return Response(data=response.json())
