from typing import Union

from django.http import HttpResponseNotFound, JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from app.models import News
from app.serializers import NewsSerializer


class NewsView(APIView):
    def get(
        self, request: Request, **kwargs
    ) -> Union[JsonResponse, HttpResponseNotFound]:
        post_list = News.objects.all()

        serialized_news_list = NewsSerializer(post_list, many=True).data
        if not serialized_news_list:
            return HttpResponseNotFound()
        return JsonResponse(serialized_news_list)
