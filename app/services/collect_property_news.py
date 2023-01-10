import json
from datetime import datetime, timedelta
from typing import Union, List, Dict

import requests
from pytz import timezone

from app.models import News
from modu_property.settings import NAVER_NEW_API_CLIENT_ID, NAVER_NEW_API_CLIENT_SECRET
from modu_property.utils.logger import logger

from bs4 import BeautifulSoup as bs


NEWS_SEARCH_KEYWORDS = [
    # "부동산",
    # "대출",
    # "금리",
    # "경매",
    "부동산 규제"
]

"""
지난 5분 동안의 부동산 뉴스를 수집함
"""


class CollectPropertyNewsService:
    # 테스트 시 뉴스 개수를 지정하기 위해 display를 인자로 받음
    def __init__(self, display: int = 100):
        self.display: int = display

    def search_news_by_naver_api(self, keyword: str) -> Union[Dict, bool]:
        try:
            headers = {
                "X-Naver-Client-Id": NAVER_NEW_API_CLIENT_ID,
                "X-Naver-Client-Secret": NAVER_NEW_API_CLIENT_SECRET,
            }
            params = {"query": keyword, "display": self.display}
            url = f"https://openapi.naver.com/v1/search/news"
            response = requests.get(url, headers=headers, params=params)
            status_code = response.status_code
            if status_code != 200:
                logger.error(f"Error Code : {status_code}")

            text = response.text
            logger.debug(text)
            loaded_data = json.loads(text)

            return loaded_data
        except Exception as e:
            logger.error(f"뉴스 못 가져옴 e : {e}")
            return False

    def insert_news(self, news_list_by_last_time: List[Dict]) -> bool:
        news_list_for_bulk_creation = []

        try:
            for news in news_list_by_last_time:
                news_list_for_bulk_creation.append(
                    News(
                        title=news["title"],
                        body=news["body"],
                        published_date=news["published_date"],
                        link=news["link"],
                    )
                )
            News.objects.bulk_create(news_list_for_bulk_creation)
            return True
        except Exception as e:
            logger.error(f"e : {e}")
            return False

    def get_detail_news_list(
        self, naver_news_list: List, detail_news_list: List
    ) -> List[Dict]:
        for naver_news in naver_news_list:
            url = naver_news.get("link")

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"
                }
                response = requests.get(url, headers=headers, timeout=0.05)
            except Exception as e:
                logger.error(f"requests.get 실패 e : {e}")
                continue

            status_code = response.status_code
            if status_code != 200:
                logger.error(
                    f"뉴스 못 가져 옴. status_code {status_code} naver_news : {naver_news}"
                )

            try:
                soup = bs(response.text, "html.parser")

                # title = soup.select_one("#title_area").text
                text = soup.select_one("#dic_area").text  # 줄바꿈 없는거
                # contents = soup.select_one("#dic_area").contents  # 줄바꿈 있는거
            except AttributeError as e:
                logger.error(f"html parse 실패 e : {e}")
                continue

            detail_news = {
                "title": naver_news["title"],
                "body": text,
                "published_date": naver_news["pubDate"],
                "link": naver_news["link"],
            }
            detail_news_list.append(detail_news)
        logger.debug(f"detail_news_list : {detail_news_list}")
        return detail_news_list

    def get_only_naver_news_list(self, data: Dict) -> List[Dict]:
        naver_news_list = []
        for item in data["items"]:
            link = item["link"]
            if "naver" in link:
                naver_news_list.append(item)

        logger.debug(f"naver new count : {len(naver_news_list)}")
        return naver_news_list

    def get_news_list_by_last_time(
        self, detail_news_list: List[Dict]
    ) -> Union[List[Dict], bool]:
        news_list_by_last_time = []
        before_format = "%a %d %b %Y %H:%M:%S %z"  # 'Sat 07 Jan 2023 17:02:00 +0900'
        after_format = "%Y-%m-%d %H:%M:%S %z"
        now = datetime.now(timezone("Asia/Seoul"))
        last_time = (now - timedelta(minutes=5)).replace()

        try:
            for detail_news in detail_news_list:
                cleaned_published_date = "".join(
                    detail_news["published_date"].split(",")
                )
                parsed_published_date = datetime.strptime(
                    cleaned_published_date, before_format
                )
                stringified_published_date = parsed_published_date.strftime(
                    after_format
                )
                published_date = datetime.strptime(
                    stringified_published_date, after_format
                )
                detail_news["published_date"] = published_date

                # 5분 전까지의 뉴스만 포함
                if last_time <= published_date:
                    news_list_by_last_time.append(detail_news)

            return news_list_by_last_time
        except Exception as e:
            logger.error(f"e : {e}")
            return False

    def execute(self) -> bool:
        detail_news_list = []
        news_list_by_last_time = [{}]
        for keyword in NEWS_SEARCH_KEYWORDS:
            data: Union[Dict, bool] = self.search_news_by_naver_api(keyword=keyword)

            if not data:
                logger.info("검색된 뉴스가 없음")
                return False

            naver_news_list: List[Dict] = self.get_only_naver_news_list(data=data)

            if not naver_news_list:
                logger.info("검색된 네이버 뉴스가 없음")
                return False

            detail_news_list: List[Dict] = self.get_detail_news_list(
                naver_news_list=naver_news_list, detail_news_list=detail_news_list
            )

            if not detail_news_list:
                return False

            news_list_by_last_time = self.get_news_list_by_last_time(
                detail_news_list=detail_news_list
            )

        result: bool = self.insert_news(news_list_by_last_time=news_list_by_last_time)

        return result
