import logging
import os
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password, make_password
from django.test import Client
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from accounts.models import User
from drf_spectacular.utils import extend_schema, OpenApiResponse

from accounts.serializers import JWTTokenSerializer, UserSerializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

logger = logging.getLogger("django")


@extend_schema(
    summary="회원가입",
    description="username, password 입력해서 회원가입",
    request=UserSerializer,
    responses={
        200: OpenApiResponse(description="회원가입 성공"),
        409: OpenApiResponse(description="이미 있는 이름입니다."),
        400: OpenApiResponse(description="회원가입 실패"),
    },
)
@api_view(("POST",))
def signup(request: Request) -> Response:
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        encrypted_password = make_password(password)
        try:
            user = User(username=username, password=encrypted_password)
            user.save()

            return Response("회원가입 성공")
        except IntegrityError as e:
            logger.error(e)
            return Response(f"{username} 이미 있는 이름입니다.", 409)
    return Response("회원가입 실패", 400)


@extend_schema(
    request=UserSerializer,
    responses={
        200: JWTTokenSerializer,
        400: OpenApiResponse(description="로그인 에러"),
        401: OpenApiResponse(description="로그인 실패"),
    },
)
@api_view(("POST",))
def login(request: Request) -> Response:
    body = request.data
    username = body.get("username", "")
    password = body.get("password", "")

    user = User.objects.get(username=username)
    is_authenticated = check_password(password, user.password)

    if is_authenticated:
        data = {
            "username": username,
            "password": password,
        }

        server_env = os.getenv("SERVER_ENV")
        response = None
        try:
            if server_env == "test":
                client = Client()
                response = client.post(path=reverse("token_obtain_pair"), data=data)
                token = response.json()

                if response.status_code != 200:
                    return Response("로그인 실패", 401)

                return Response(
                    data={
                        "access_token": token["access"],
                        "refresh_token": token["refresh"],
                    }
                )
            else:
                token = TokenObtainPairSerializer.get_token(user)
                refresh_token = str(token)
                access_token = str(token.access_token)

                return Response(
                    data={"access_token": access_token, "refresh_token": refresh_token}
                )

        except Exception as e:
            logger.error(f"로그인 에러 : {e}")
            return Response("로그인 에러", status=400)
