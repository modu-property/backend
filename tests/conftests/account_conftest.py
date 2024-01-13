import datetime
import jwt
import pytest

from modu_property.settings.test_settings import SECRET_KEY
from django.contrib.auth.hashers import make_password
from accounts.models import User


@pytest.fixture
def get_jwt():
    return jwt.encode(
        {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
            # "user_id": 1,
        },
        SECRET_KEY,
        algorithm="HS256",
    )


@pytest.fixture
def create_user():
    def _create_user(username: str, password: str):
        encrypted_password = make_password(str(password))
        user = User(username=username, password=encrypted_password)

        user.save()
        return user

    return _create_user
