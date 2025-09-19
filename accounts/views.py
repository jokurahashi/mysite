from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # ユーザー保存
            user = form.save(commit=False)
            raw_password = form.cleaned_data["password1"]
            user.set_password(raw_password)  # パスワードをハッシュ化して保存
            user.save()

            # 登録完了画面
            return render(request, "home.html", {
                "user": user,
                "raw_password": raw_password,  # パスワード表示用
            })
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})