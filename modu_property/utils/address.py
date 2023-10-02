# import os
# from typing import Union
# import requests


# class AddressUtil:
#     def __init__(self) -> None:
#         pass
    
#     def get_address_info(self, dong: str, lot_number: str) -> Union[dict, bool]:
#         headers = {
#             "Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}" 
#         }
#         params = {
#             "query": f"{dong} {lot_number}"
#         }
#         response = requests.get("https://dapi.kakao.com/v2/local/search/address.json", headers=headers, params=params)

#         if response.status_code != 200:
#             print("카카오 주소 변환 실패")
#             return False
        
#         documents = response.json()['documents']
        
#         if not documents:
#             print("documents 없음")
#             return False
        
#         document = documents[0]
#         road_name_address = document['road_address']['address_name']
#         latitude = document['road_address']['x']
#         longitude = document['road_address']['y']

#         return {
#             "road_name_address": road_name_address,
#             "latitude": latitude,
#             "longitude": longitude
#         }
