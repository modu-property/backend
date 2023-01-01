from django.urls import path
from accounts.views import login, signup

urlpatterns = [path("login/", login), path("signup/", signup)]
