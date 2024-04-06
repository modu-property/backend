from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class JWTTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=256)
    refresh_token = serializers.CharField(max_length=256)
