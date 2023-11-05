from typing import Union
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from accounts.util.authenticator import jwt_authenticator
from property.dto.villa_dto import GetDealPriceOfVillaDto
from property.serializers import GetVillaRequestSerializer
from property.services.get_deal_price_of_villa_service import GetDealPriceOfVillaService


class VillaView(ListAPIView):
    """
    TODO
    * 위경도+줌레벨, 검색어+줌레벨 받기
    * 검색어면 위경도로 변환
    * 위경도 기준으로 줌레벨에 맞는 반경 n킬로미터에 있는 빌라 매물 정보 가져오기
    """

    @jwt_authenticator
    def get(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Union[HttpResponse, HttpResponseNotFound]:
        # search tab에서 검색할 때/지도 이동할 때 나오는 빌라 주소 정보

        request_data = {
            "id": request.query_params.get("id", 0) and int(request.query_params["id"]),
            "type": kwargs["type"],
            "latitude": request.query_params.get("latitude", 0.0),
            "longitude": request.query_params.get("longitude", 0.0),
            "zoom_level": request.query_params.get("zoom_level", 0),
            "keyword": request.query_params.get("keyword", ""),
        }
        serializer = GetVillaRequestSerializer(data=request_data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            dto = GetDealPriceOfVillaDto(**validated_data)
            villas_response_serializer = GetDealPriceOfVillaService().execute(dto=dto)

            if not villas_response_serializer:
                return JsonResponse(data={}, status=404)

            if villas_response_serializer.is_valid():
                return JsonResponse(
                    data=villas_response_serializer.validated_data,
                    status=200,
                    safe=False,
                )

            # # TODO : response 메서드 만들기
            # if message == "검색 결과 없음":
            #     return JsonResponse(
            #         data={"villas": villas, "message": message}, status=404
            #     )
            # elif message == "빌라 찾음":
            #     return JsonResponse(
            #         data={"villas": villas, "message": message}, status=200
            #     )
            # elif message in "Exception when calling SearchApi->search e:":
            #     return JsonResponse(
            #         data={"villas": villas, "message": message}, status=400
            #     )
            # elif message in "VillaView get e:":
            #     return JsonResponse(
            #         data={"villas": villas, "message": message}, status=400
            #     )
