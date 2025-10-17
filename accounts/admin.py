from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # ユーザー一覧に表示するフィールド
    list_display = (
        "username",
        "email",
        "birthday",
        "is_staff",
        "is_superuser",
        "is_deleted",
    )
    # ユーザー追加・編集画面で使うフィールド
    fieldsets = (
        (None, {"fields": ("username", "email", "password", "birthday")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "is_superuser", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "birthday",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    ordering = ("username",)

    # 論理削除にする
    def delete_model(self, request, obj):
        obj.delete()  # CustomUser.delete() が呼ばれるので論理削除になる

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
