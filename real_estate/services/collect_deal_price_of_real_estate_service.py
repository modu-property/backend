import json
import logging
import os
from typing import Union
from django.forms import model_to_dict
from django.contrib.gis.geos import Point
import requests
import xmltodict
from modu_property.utils.validator import validate_model

from real_estate.models import Deal, RealEstate
from real_estate.serializers import DealSerializer, RealEstateSerializer

"""
일단 한 클래스에서 수집하고 나중에 필요하면 아파트, 빌라별로 클래스 생성
"""


class CollectDealPriceOfRealEstateService:
    def __init__(self, url: str, type: str) -> None:
        self.url = url
        self.type = type
        self.service_key = os.getenv("SERVICE_KEY")
        self.logger = logging.getLogger("django")

    def collect_deal_price_of_real_estate(
        self, params: dict
    ) -> Union[list[dict], bool]:
        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            content: dict = xmltodict.parse(response.content, encoding="utf-8")

            # Convert dictionary to JSON
            json_response: json = json.loads(json.dumps(content, indent=4))

            return json_response["response"]["body"]["items"]["item"]

        print(response.status_code, "get_deal_price_of_real_estate 수집 실패")

        return False

    def get_address_info(self, dong: str, lot_number: str) -> Union[dict, bool]:
        headers = {"Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}"}
        params = {"query": f"{dong} {lot_number}"}
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            print("카카오 주소 변환 실패")
            return False

        documents = response.json()["documents"]

        if not documents:
            print("documents 없음")
            return False

        document = documents[0]
        road_name_address = document["road_address"]["address_name"]
        latitude = document["road_address"]["y"]
        longitude = document["road_address"]["x"]

        return {
            "road_name_address": road_name_address,
            "latitude": latitude,
            "longitude": longitude,
        }

    def execute(self, dong_code, deal_ymd):
        ## LAWD_CD : 지역코드. https://www.code.go.kr/index.do 의 법정동코드 10자리 중 앞 5자리
        # 1111000000 이렇게 동까지 지정하면???
        params = {
            "serviceKey": self.service_key,
            "LAWD_CD": dong_code,
            "DEAL_YMD": deal_ymd,
        }
        deal_prices_of_real_estate = self.collect_deal_price_of_real_estate(
            params=params
        )

        if not deal_prices_of_real_estate:
            return

        real_estate_models = []
        deal_models = []
        for deal_price_of_real_estate in deal_prices_of_real_estate:
            # bulk_create를 하면 유효성 검사가 안되므로 미리 확인하고 진행해야함.
            address_info = self.get_address_info(
                dong=deal_price_of_real_estate["법정동"],
                lot_number=deal_price_of_real_estate["지번"],
            )

            real_estate_model = RealEstate(
                name=deal_price_of_real_estate["연립다세대"],
                build_year=deal_price_of_real_estate["건축년도"],
                regional_code=deal_price_of_real_estate["지역코드"],
                lot_number=deal_price_of_real_estate["지번"],
                road_name_address=address_info["road_name_address"],
                latitude=address_info["latitude"],
                longitude=address_info["longitude"],
                point=Point(
                    float(address_info["latitude"]), float(address_info["longitude"])
                ),
            )

            real_estate_dict = model_to_dict(real_estate_model)

            validated_real_estate = validate_model(
                model=real_estate_model,
                data=real_estate_dict,
                serializer=RealEstateSerializer,
            )
            if not validated_real_estate:
                print(
                    f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                )
                return False

            real_estate_models.append(RealEstate(**validated_real_estate))

            inserted_real_estate_models = []
            try:
                if real_estate_models:
                    inserted_real_estate_models = RealEstate.objects.bulk_create(
                        real_estate_models
                    )
            except Exception as e:
                print(f"real_estate bulk_create params : {params}, e : {e}")
                return False

            for inserted_real_estate_model in inserted_real_estate_models:
                deal_model = Deal(
                    deal_price=deal_price_of_real_estate["거래금액"],
                    deal_type=deal_price_of_real_estate["거래유형"],
                    deal_year=deal_price_of_real_estate["년"],
                    land_area=deal_price_of_real_estate["대지권면적"],
                    deal_month=deal_price_of_real_estate["월"],
                    deal_day=deal_price_of_real_estate["일"],
                    area_for_exclusive_use=deal_price_of_real_estate["전용면적"],
                    floor=deal_price_of_real_estate["층"],
                    is_deal_canceled=deal_price_of_real_estate["해제여부"],
                    deal_canceled_date=deal_price_of_real_estate["해제사유발생일"],
                    type=self.type,
                    real_estate_id=inserted_real_estate_model.id,
                )

                deal_dict = model_to_dict(deal_model)

                validated_deal = validate_model(
                    model=deal_model,
                    data=deal_dict,
                    serializer=DealSerializer,
                )
                if not validated_deal:
                    print(
                        f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                    )
                    return False

                deal_models.append(Deal(**validated_deal))

            try:
                if deal_models:
                    Deal.objects.bulk_create(deal_models)
                    return True
            except Exception as e:
                print(f"deal bulk_create params : {params}, e : {e}")
                return False
