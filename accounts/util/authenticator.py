import jwt
from rest_framework.response import Response

from modu_property.test_settings import SIMPLE_JWT


def jwt_authenticator(fn):
    def wrapper(self, request, *args, **kwargs):
        try:
            jwt_token = request.headers.get("Authorization")
            decoded_jwt = jwt.decode(
                jwt=jwt_token,
                key=SIMPLE_JWT["SIGNING_KEY"],
                algorithms=SIMPLE_JWT["ALGORITHM"],
            )
            user_id = decoded_jwt["user_id"]

            return fn(self, request, user_id=user_id, *args, **kwargs)
        except:
            return Response("jwt 오류", status=401)

    return wrapper
