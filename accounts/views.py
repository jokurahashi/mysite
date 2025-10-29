from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import CustomUser
from django.contrib import messages
from django.db.models import Q
import csv
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date


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

    # 検索機能(検索処理を行う、空白だと全件表示させる)
    username_query = request.GET.get("username", "").strip()
    email_query = request.GET.get("email", "").strip()
    created_from = request.GET.get("created_from", "")
    created_to = request.GET.get("created_to", "")
    updated_from = request.GET.get("updated_from", "")
    updated_to = request.GET.get("updated_to", "")

    users = CustomUser.objects.all().order_by("-updated_at", "-created_at")

    # 検索機能(検索処理を行う、空白だと全件表示させる)

    if username_query:  # 大文字と小文字の区別を行う
        users = users.filter(username__contains=username_query)
    if email_query:  # メールアドレスは大文字と小文字の区別を行わない
        users = users.filter(email__icontains=email_query)

    # 日付で絞り込み
    if created_from:
        users = users.filter(created_at__gte=parse_date(created_from))
    if created_to:
        users = users.filter(created_at__lte=parse_date(created_to))
    if updated_from:
        users = users.filter(updated_at__gte=parse_date(updated_from))
    if updated_to:
        users = users.filter(updated_at__lte=parse_date(updated_to))

    context = {
        "users": users,
        "username_query": username_query,
        "email_query": email_query,
        "created_from": created_from,
        "created_to": created_to,
        "updated_from": updated_from,
        "updated_to": updated_to,
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
    # GET パラメータから検索条件を取得
    username_query = request.GET.get("username", "").strip()
    email_query = request.GET.get("email", "").strip()
    created_from_date = request.GET.get("created_from", "").strip()
    created_to_date = request.GET.get("created_to", "").strip()
    updated_from_date = request.GET.get("updated_from", "").strip()
    updated_to_date = request.GET.get("updated_to", "").strip()

    # フィルタ条件を組み立てる
    users = User.objects.filter(
        Q(username__icontains=username_query) if username_query else Q(),
        Q(email__icontains=email_query) if email_query else Q(),
        Q(created_at__gte=created_from_date) if created_from_date else Q(),
        Q(created_at__lte=created_to_date) if created_to_date else Q(),
        Q(updated_at__gte=updated_from_date) if updated_from_date else Q(),
        Q(updated_at__lte=updated_to_date) if updated_to_date else Q(),
    ).order_by("-updated_at", "-created_at")

    # CSVを生成
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(
        ["ID", "ユーザー名", "メールアドレス", "誕生日", "作成日時", "更新日時"]
    )
    for user in users:
        writer.writerow(
            [
                user.username,
                user.email,
                user.birthday,
                user.created_at,
                user.updated_at,
            ]
        )

    return response


# CSVインポート機能
def import_users_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        # CSVチェック
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "CSVファイルを選択してください。")
            return redirect("accounts:user_list")

        # ファイル読み込み
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        # ヘッダー検証
        expected_headers = ["Username", "Email"]
        if reader.fieldnames != expected_headers:
            messages.error(
                request,
                "CSVヘッダーが正しくありません。",
            )
            return redirect("accounts:user_list")

        success_count = 0
        error_count = 0

        # 各行を検証しながら登録
        for i, row in enumerate(reader, start=2):  # 2行目からデータ開始
            username = row.get("Username", "").strip()
            email = row.get("Email", "").strip()

            # 必須項目チェック
            if not username or not email:
                messages.warning(
                    request, f"{i}行目: ユーザー名またはメールアドレスが空です。"
                )
                error_count += 1
                continue

            # メール形式チェック
            try:
                validate_email(email)
            except ValidationError:
                messages.warning(
                    request, f"{i}行目: メールアドレス形式が不正です。({email})"
                )
                error_count += 1
                continue

            # 既存ユーザー重複チェック
            if User.objects.filter(username=username).exists():
                messages.info(
                    request,
                    f"{i}行目: ユーザー '{username}' は既に存在します。スキップしました。",
                )
                continue

            # 作成
            User.objects.create(username=username, email=email)
            success_count += 1

    return redirect("accounts:user_list")
