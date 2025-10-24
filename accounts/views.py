from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import CustomUser
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.contrib.auth import get_user_model


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
    users = CustomUser.objects.all().order_by("-updated_at", "-created_at")

    # 検索機能(検索処理を行う、空白だと全件表示させる)
    username_query = request.GET.get("username", "")
    email_query = request.GET.get("email", "")

    if username_query:  # 大文字と小文字の区別を行う
        users = users.filter(username__contains=username_query)
    if email_query:  # メールアドレスは大文字と小文字の区別を行わない
        users = users.filter(email__icontains=email_query)

    context = {
        "users": users,
        "username_query": username_query,
        "email_query": email_query,
    }
    return render(request, "accounts/user_list.html", context)


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
    context = {"form": form, "user": user}
    return render(request, "accounts/user_edit.html", context)


# ユーザー削除(論理削除)
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        user.is_deleted = True  # 論理削除
        user.save()
        messages.success(request, "ユーザーを削除しました")
        return redirect("accounts:user_detail", pk=user.pk)  # 詳細に戻る
    return render(request, "accounts/user_delete.html", {"user": user})


User = get_user_model()


# CSVダウンロード機能
def export_users_csv(request):
    # 全ユーザーを取得
    users = User.objects.all()
    # CSVを生成
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Username", "Email", "Created At"])
    for user in users:
        writer.writerow(
            [
                user.id,
                user.username,
                user.email,
                (
                    user.date_joined.strftime("%Y-%m-%d %H:%M:%S")
                    if user.date_joined
                    else ""
                ),
            ]
        )
    return response


# CSVインポート機能
def import_users_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith(".csv"):
            return redirect("accounts:user_list")
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)
        count = 0
        for row in reader:
            username = row.get("Username")
            email = row.get("Email")
            if username and email:
                # 既存ユーザーは作らない、存在しなければ作成
                User.objects.get_or_create(username=username, defaults={"email": email})
                count += 1
    return redirect("accounts:user_list")
