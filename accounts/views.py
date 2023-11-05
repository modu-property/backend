import os
from django.db import IntegrityError
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
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from accounts.serializers import UserSerializer


@extend_schema(
    summary="회원가입",
    description="username, password 입력해서 회원가입. multipart/form-data",
    request=UserSerializer,
    responses={
        200: OpenApiResponse(description="회원가입 성공"),
        409: OpenApiResponse(description="{} 이미 있는 이름입니다."),
        400: OpenApiResponse(description="회원가입 실패"),
    },
)
@api_view(("POST",))
def signup(request: Request) -> Response:
    print(request.POST)
    serializer = UserSerializer(data=request.POST)

    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        encrypted_password = make_password(password)
        try:
            user = User(username=username, password=encrypted_password)
            user.save()

            return Response("회원가입 성공")
        except IntegrityError as e:
            print(e)
            return Response(f"{username} 이미 있는 이름입니다.", 409)
    return Response("회원가입 실패", 400)


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
