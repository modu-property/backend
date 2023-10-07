from typing import Union

from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from rest_framework.request import Request
from rest_framework.views import APIView
from accounts.util.authenticator import jwt_authenticator
from property.dto.villa_dto import GetDealPriceOfVillaDto

from property.models import Villa
from property.serializers import GetVillaRequestSerializer
from property.services.get_deal_price_of_villa_service import GetDealPriceOfVillaService

# from property.serializers import NewsSerializer


class VillaView(APIView):
    @jwt_authenticator
    def get(
        self,
        request: Request,
        user_id,
        *args,
        **kwargs,
    ) -> Union[HttpResponse, HttpResponseNotFound]:
        """
        TODO
        * 위경도+줌레벨, 검색어+줌레벨 받기
        * 검색어면 위경도로 변환
        * 위경도 기준으로 줌레벨에 맞는 반경 n킬로미터에 있는 빌라 매물 정보 가져오기

        postgresql 써야하나?
        mysql에 위경도로 거리 계산하는거 있는지 확인 필요!
        """
        request_data = {
            "type": kwargs["type"],
            "latitude": request.query_params["latitude"],
            "longitude": request.query_params["longitude"],
            "zoom_level": request.query_params["zoom_level"],
            "keyword": request.query_params["keyword"],
        }
        serializer = GetVillaRequestSerializer(data=request_data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            dto = GetDealPriceOfVillaDto(**validated_data)
            GetDealPriceOfVillaService().execute(dto=dto)

        return JsonResponse()
        post_list = News.objects.all()

        serialized_news_list = NewsSerializer(post_list, many=True).data
        if not serialized_news_list:
            return HttpResponseNotFound()
        return JsonResponse(serialized_news_list, safe=False)
