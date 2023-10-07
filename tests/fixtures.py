import jwt
import datetime
import pytest

# from app.models import News
from modu_property.test_settings import SECRET_KEY


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


# @pytest.fixture
# def create_news(title: str = "test_title", body: str = "test_body"):
#     news = News(
#         title=title,
#         body=body,
#         published_date=datetime.datetime.utcnow(),
#         link="https://n.news.naver.com/mnews/article/001/0013688002?sid=101",
#     )
#     news.save()

#     return news
