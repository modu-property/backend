from decimal import Decimal
import json
import os
from typing import Union
from django.forms import model_to_dict
import requests
import xmltodict

from real_estate.models import RealEstate
from real_estate.serializers import RealEstateSerializer
from rest_framework.exceptions import ValidationError


class CollectDealPriceOfRealEstateService:
    def __init__(self) -> None:
        self.url = os.getenv("DEAL_PRICE_OF_REAL_ESTATE_API")
        self.service_key = os.getenv("SERVICE_KEY")

    def get_deal_price_of_real_estate(self, params: dict) -> Union[list[dict], bool]:
        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            content: dict = xmltodict.parse(response.content, encoding="utf-8")

            # Convert dictionary to JSON
            json_response: json = json.loads(json.dumps(content, indent=4))

            return json_response["response"]["body"]["items"]["item"]

        print(response.status_code, "빌라 실거래가 수집 실패")

        return False

    def convert_square_meter_to_pyung(self, square_meter: str) -> Decimal:
        return round(Decimal(square_meter) / Decimal(3.305785), 2)

    def calc_price_per_pyung(self, deal_price: int, pyung: Decimal) -> Decimal:
        return round(deal_price / pyung, 2)

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
        latitude = document["road_address"]["x"]
        longitude = document["road_address"]["y"]

        return {
            "road_name_address": road_name_address,
            "latitude": latitude,
            "longitude": longitude,
        }

    def validate_real_estate_model(
        self, real_estate_model: RealEstate, real_estate_dict: dict
    ) -> Union[dict, bool]:
        try:
            serializer = RealEstateSerializer(
                instance=real_estate_model, data=real_estate_dict
            )

            if not serializer.is_valid(raise_exception=True):
                return False

            serializer.initial_data
            serializer.validated_data
            data = serializer.data

            return data
        except ValueError as e:
            print(
                f"validate_real_estate_model ValueError e : {e}, real_estate_dict : {real_estate_dict}"
            )
            return False
        except ValidationError as e:
            print(
                f"validate_real_estate_model ValidationError e : {e}, real_estate_dict : {real_estate_dict}"
            )
            return False
        except Exception as e:
            print(f"validate_real_estate_model e : {e}")
            return False

    def execute(self):
        ## LAWD_CD : 지역코드. https://www.code.go.kr/index.do 의 법정동코드 10자리 중 앞 5자리
        # 1111000000 이렇게 동까지 지정하면???
        params = {
            "serviceKey": self.service_key,
            "LAWD_CD": "11110",
            "DEAL_YMD": "201512",
        }

        deal_prices_of_real_estate = self.get_deal_price_of_real_estate(params=params)

        if not deal_prices_of_real_estate:
            return

        deal_price_of_real_estate_models = []
        for deal_price_of_real_estate in deal_prices_of_real_estate:
            # bulk_create를 하면 유효성 검사가 안되므로 미리 확인하고 진행해야함.
            address_info = self.get_address_info(
                dong=deal_price_of_real_estate["법정동"],
                lot_number=deal_price_of_real_estate["지번"],
            )

            real_estate_model = RealEstate(
                deal_price=deal_price_of_real_estate["거래금액"],
                deal_type=deal_price_of_real_estate["거래유형"],
                build_year=deal_price_of_real_estate["건축년도"],
                deal_year=deal_price_of_real_estate["년"],
                land_area=deal_price_of_real_estate["대지권면적"],
                dong=deal_price_of_real_estate["법정동"],
                name=deal_price_of_real_estate["연립다세대"],
                deal_month=deal_price_of_real_estate["월"],
                deal_day=deal_price_of_real_estate["일"],
                area_for_exclusive_use=deal_price_of_real_estate["전용면적"],
                lot_number=deal_price_of_real_estate["지번"],
                regional_code=deal_price_of_real_estate["지역코드"],
                floor=deal_price_of_real_estate["층"],
                is_deal_canceled=deal_price_of_real_estate["해제여부"],
                deal_canceled_date=deal_price_of_real_estate["해제사유발생일"],
                broker_address=deal_price_of_real_estate["중개사소재지"],
                road_name_address=address_info["road_name_address"],
                latitude=address_info["latitude"],
                longitude=address_info["longitude"],
            )

            real_estate_dict = model_to_dict(real_estate_model)

            validated_real_estate = self.validate_real_estate_model(
                real_estate_model=real_estate_model, real_estate_dict=real_estate_dict
            )
            if not validated_real_estate:
                print(
                    f"유효성 검사 실패 deal_price_of_real_estate : {deal_price_of_real_estate}"
                )
                continue

            deal_price_of_real_estate_models.append(RealEstate(**validated_real_estate))

        try:
            if deal_price_of_real_estate_models:
                RealEstate.objects.bulk_create(deal_price_of_real_estate_models)
            return True
        except Exception as e:
            print(f"real_estate bulk_create params : {params}, e : {e}")
            return False
