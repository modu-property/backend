import json
from typing import Union, List, Dict

import requests

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


class CollectPropertyNewsService:
    def __init__(self):
        self.display = 50

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

    def insert_news(self, detail_news_list: List[Dict]) -> bool:
        # TODO : title, pubdate, link, description, 등 저장... news 모델 설계해야함
        news_list_for_bulk_creation = []
        try:
            for detail_news in detail_news_list:
                news = News(
                    title=detail_news["title"],
                    body=detail_news["body"],
                    published_date=detail_news["published_date"],
                    link=detail_news["link"],
                )
                news_list_for_bulk_creation.append(news)
            News.objects.bulk_create(news_list_for_bulk_creation)
            return True
        except Exception as e:
            pass
            return False

    def get_detail_news_list(self, naver_news_list: List) -> List[Dict]:
        detail_news_list = []

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

                title = soup.select_one("#title_area").text
                text = soup.select_one("#dic_area").text
                contents = soup.select_one("#dic_area").contents
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

    def execute(self):
        """
        TODO
        매 5분마다 지난 5분동안 게시된 뉴스를 가져오고, 본문까지 긁어와서 DB에 저장
        command 대신 service로 로직 빼고, celery beat 사용해야 함
        """
        news = [{}]
        for keyword in NEWS_SEARCH_KEYWORDS:
            data: Union[Dict, bool] = self.search_news_by_naver_api(keyword)

            if not data:
                logger.info("검색된 뉴스가 없음")
                break

            naver_news_list: List[Dict] = self.get_only_naver_news_list(data)

            if not naver_news_list:
                logger.info("검색된 네이버 뉴스가 없음")
                break

            detail_news_list: List[Dict] = self.get_detail_news_list(naver_news_list)

            if not detail_news_list:
                return

        self.insert_news(detail_news_list=detail_news_list)
