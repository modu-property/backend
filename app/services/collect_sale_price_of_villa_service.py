import json
import os
import requests
import xmltodict

class CollectSalePriceOfVillaService:
    def __init__(self) -> None:
        self.url = os.getenv("SALE_PRICE_OF_VILLA_API")
        self.service_key = os.getenv("SERVICE_KEY")

    def execute(self):
        ## LAWD_CD : 지역코드. https://www.code.go.kr/index.do 의 법정동코드 10자리 중 앞 5자리
        # 1111000000 이렇게 동까지 지정하면???
        params = {'serviceKey' : self.service_key, 'LAWD_CD' : '11110', 'DEAL_YMD' : '201512' }

        response = requests.get(self.url, params=params)

        xml_dict = xmltodict.parse(response)

        # Convert dictionary to JSON
        json_response = json.dumps(xml_dict, indent=4)
        print(json_response)

        # model 만들고 dict -> model에 매핑한다음 bulk insert 하기
        