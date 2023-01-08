from typing import Union

from django.http import HttpResponseNotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import News
from app.serializers import NewsSerializer


class NewsView(APIView):
    def get(self, request: Request, **kwargs) -> Union[Response, HttpResponseNotFound]:
        post_list = News.objects.all()

        serialized_news_list = NewsSerializer(post_list, many=True).data
        if not serialized_news_list:
            return HttpResponseNotFound()
        return Response(serialized_news_list)
