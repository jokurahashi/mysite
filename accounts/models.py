from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="ユーザー名",
        error_messages={
            "unique": "同じユーザー名が既に登録済みです。",
        } 
    )
    email = models.EmailField(
        unique=True,
        verbose_name="メールアドレス",
        error_messages={
            "unique": "このメールアドレスはすでに登録されています。",
            "invalid": "有効なメールアドレスを入力してください。",
        }
    )
    birthday = models.DateField(
        verbose_name="誕生日",
        null=True,
        blank=True,
    )
    is_deleted = models.BooleanField(default=False, verbose_name="削除フラグ")

    def __str__(self):
        return self.username

    # 論理削除
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.is_active = False
        self.save()
