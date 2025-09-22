from django.urls import path
from . import views

app_name = "accounts"  # ← 名前空間を必ず設定

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),

]

