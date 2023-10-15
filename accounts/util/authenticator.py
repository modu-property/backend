import os
import jwt
from rest_framework.response import Response


def jwt_authenticator(fn):
    def wrapper(self, request, *args, **kwargs):
        try:
            jwt_token = request.headers.get("Authorization").split("Bearer ")[1]
            decoded_jwt = jwt.decode(
                jwt=jwt_token,
                key=os.getenv("SECRET_KEY"),
                algorithms="HS256",
            )

            return fn(self, request, *args, **kwargs)
        except Exception as e:
            print(f"jwt_authenticator e : {e}")
            return Response(f"jwt 오류 e : {e}", status=401)

    return wrapper
