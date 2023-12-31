import os
import jwt
from rest_framework.response import Response

from modu_property.utils.loggers import logger


def jwt_authenticator(fn):
    def wrapper(self, request, *args, **kwargs):
        try:
            auth = request.headers.get("Authorization", "")
            if not auth:
                raise PermissionError("header에 Authorization 없음")
            jwt_token = request.headers.get("Authorization").split("Bearer ")[1]
            decoded_jwt = jwt.decode(
                jwt=jwt_token,
                key=os.getenv("SECRET_KEY"),
                algorithms="HS256",
            )

            return fn(self, request, *args, **kwargs)
        except Exception as e:
            logger.error(f"jwt_authenticator e : {e}")
            return Response(f"jwt 오류 e : {e}", status=401)

    return wrapper
