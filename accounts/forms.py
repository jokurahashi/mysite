# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
import datetime

class CustomUserCreationForm(UserCreationForm):
    # 確認用パスワードは削除
    password2 = None

    # パスワードフィールド
    password1 = forms.CharField(
        label="パスワード",
        strip=False,
        widget=forms.PasswordInput,
        help_text="",
    )

    # メールアドレスを必須＆type=emailにする
    email = forms.EmailField(
        label="メールアドレス",
        required=True,
        widget=forms.EmailInput(),
        error_messages={
            "unique": "このメールアドレスはすでに登録されています。",
            "invalid": "正しいメールアドレスを入力してください。",
        }
    )

    # 誕生日フィールド
    birthday = forms.DateField(
        label="誕生日",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "birthday")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # help_text を消す
        for field in self.fields.values():
            field.help_text = ""

        # ユーザー名エラー文
        self.fields["username"].error_messages.update({
            "unique": "同じユーザー名が既に登録済みです。",
        })


    # パスワード独自バリデーション
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise ValidationError("パスワードは8文字以上にしてください。")
        if password.isdigit():
            raise ValidationError("パスワードを数字だけにすることはできません。")
        if password.lower() in ["password", "12345678", "qwerty"]:
            raise ValidationError("パスワードが簡単すぎます。別のものを入力してください。")
        return password

    # 誕生日バリデーション
    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")
        if birthday > datetime.date.today():
            raise ValidationError("未来の日付は誕生日に指定できません。")
        return birthday
    

# accounts/forms.py の末尾に追加
from django import forms
from .models import CustomUser

class CustomUserUpdateForm(forms.ModelForm):
    """
    ユーザー編集・論理削除用フォーム
    - username, email, birthday を編集可能
    - is_deleted を操作して論理削除できる
    """
    class Meta:
        model = CustomUser
        fields = ["username", "email", "birthday", "is_deleted"]
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "username": "ユーザー名",
            "email": "メールアドレス",
            "birthday": "誕生日",
            "is_deleted": "削除済み",
        }

class CustomUserEditForm(forms.ModelForm):
    """ユーザー編集用フォーム"""
    class Meta:
        model = CustomUser
        fields = ("username", "email", "birthday")