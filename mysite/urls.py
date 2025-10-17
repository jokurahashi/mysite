from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # ルートにアクセスしたら signup にリダイレクト
    path("", lambda request: redirect("accounts:signup"), name="root_redirect"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # ← namespace を追加
]
