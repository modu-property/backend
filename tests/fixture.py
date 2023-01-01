import datetime

import jwt
import pytest

from app.models import Post
from mysite.settings import SECRET_KEY


@pytest.fixture
def get_jwt():
    return jwt.encode(
        {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            "user_id": 1,
        },
        SECRET_KEY,
        algorithm="HS256",
    )


@pytest.fixture
def create_post():
    post = Post(title="test_title", content="test_content")
    return post.save()
