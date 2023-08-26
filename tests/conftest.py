# from pytz import timezone

# from tests.fixtures import *
# from datetime import datetime


# @pytest.fixture
# def mock_search_news_by_naver_api():
#     def _mock_search_news_by_naver_api(**kwargs):
#         changed_format = "%a, %d %b %Y %H:%M:%S %z"
#         now = datetime.now(timezone("Asia/Seoul"))
#         stringified_datetime = datetime.strftime(now, changed_format)

#         return {
#             "lastBuildDate": "Sat, 07 Jan 2023 22:50:51 +0900",
#             "total": 663501,
#             "start": 1,
#             "display": 1,
#             "items": [
#                 {
#                     "title": "“10억 마지노선 무너졌다”...위례신도시에 무슨 일이",
#                     "originallink": "https://www.mk.co.kr/article/10597684",
#                     "link": "https://n.news.naver.com/mnews/article/024/0000079352?sid=101",
#                     "description": "<b>부동산</b>업계 관계자는 “서울 강남권마저 집값이 급락하는 상황에서 위례신도시도 한파를 피하지 못했다”면서도 “정부가 대출, 세금 <b>규제</b>를 완화한 데다 위례선 도시철도 등 교통 호재가 진행 중인 만큼 위례... ",
#                     "pubDate": stringified_datetime,
#                 },
#                 {
#                     "title": "test",
#                     "originallink": "https://www.mk.co.kr/article/10597684",
#                     "link": "https://n.news.naver.com/mnews/article/024/0000079352?sid=101",
#                     "description": "<b>부동산</b>업계 관계자는 “서울 강남권마저 집값이 급락하는 상황에서 위례신도시도 한파를 피하지 못했다”면서도 “정부가 대출, 세금 <b>규제</b>를 완화한 데다 위례선 도시철도 등 교통 호재가 진행 중인 만큼 위례... ",
#                     "pubDate": "Sat, 07 Jan 2023 21:17:00 +0900",
#                 },
#             ],
#         }

#     return _mock_search_news_by_naver_api
