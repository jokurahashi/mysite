from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .forms import CustomUserEditForm
from .models import CustomUser
from django.contrib import messages


# ユーザー登録ビュー
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # ユーザー保存
            user = form.save(commit=False)
            raw_password = form.cleaned_data["password1"]
            user.set_password(raw_password)  # パスワードをハッシュ化
            user.save()

            messages.success(request, "登録が完了しました")

            # ユーザー一覧画面へリダイレクト
            return redirect("accounts:user_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


# ユーザー一覧ビュー
def user_list(request):
    users = CustomUser.objects.all()
    users = CustomUser.objects.order_by("-created_at")  # ← 作成日時の降順
    users = CustomUser.objects.all().order_by("-updated_at")  # 更新日時の降順
    return render(request, "accounts/user_list.html", {"users": users})


from .forms import CustomUserUpdateForm


# ユーザー詳細
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    return render(
        request,
        "accounts/user_detail.html",
        {
            "user": user,
        },
    )


# ユーザー編集
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":  # フォームが送信された場合
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "ユーザー情報を編集しました")
            return redirect("accounts:user_detail", pk=user.pk)  # 詳細に戻る
    else:
        form = CustomUserEditForm(instance=user)
    return render(request, "accounts/user_edit.html", {"form": form, "user": user})


# ユーザー削除(論理削除)
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        user.is_deleted = True  # 論理削除
        user.save()
        messages.success(request, "ユーザーを削除しました")
        return redirect("accounts:user_detail", pk=user.pk)  # 詳細に戻る
    return render(request, "accounts/user_delete.html", {"user": user})
