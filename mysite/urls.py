from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),  
    # ルートにアクセスしたら signup にリダイレクト
    path("", lambda request: redirect("signup"), name="root_redirect"),
    path("accounts/", include("accounts.urls")),
]





