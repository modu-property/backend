"""
클라이언트로부터 검색어 받기
검색어에 해당하는 위경도 구하기
위경도 반경 몇미터에 있는 빌라들 구해서 응답하기

"""

from property.dto.villa_dto import GetDealPriceOfVillaDto


class GetDealPriceOfVillaService:
    def __init__(self) -> None:
        pass

    def execute(self, dto: GetDealPriceOfVillaDto):
        # zoom_level에 맞게 반경 지정하는 메서드 만들기
        # keyword가 있으면 그 검색어에 맞는 거 추출(manticore 사용?)하고 그곳의 latitude, longitude 구해서 반경 내에 속하는 것들 추출
        # keyword 없고 latitude, longitude 있으면  반경 내에 속하는 것들 추출
        return True
