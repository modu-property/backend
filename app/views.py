from typing import Union

from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.util.authenticator import jwt_authenticator
from app.forms import PostForm
from app.models import Post
from app.serializers import PostSerializer


class PostView(APIView):
    @jwt_authenticator
    def post(
        self, request: Request, *args, **kwargs
    ) -> Union[Response, HttpResponseBadRequest]:
        if kwargs["user_id"]:
            post_form = PostForm(request.POST)

            if post_form.is_valid():
                post = post_form.save()
                serialized_post = PostSerializer(post).data
                return Response(serialized_post)

        return HttpResponseBadRequest()

    def get(self, request: Request, **kwargs) -> Union[Response, HttpResponseNotFound]:
        if kwargs.get("id") is None:
            post_list = Post.objects.all()

            serialized_post_list = PostSerializer(post_list, many=True).data
            if not serialized_post_list:
                return HttpResponseNotFound()
            return Response(serialized_post_list)

        id = kwargs.get("id")
        post = get_object_or_404(Post, id=id)
        serialized_post = PostSerializer(post).data
        response = Response(serialized_post)
        return response
