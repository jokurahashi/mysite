import pytest
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser


@pytest.mark.django_db
class TestUserDetailView:
    def test_user_detail_displays_correct_user(self, client):
        """ユーザー詳細ページに正しいユーザー情報が表示されることを確認"""
        # テストユーザー作成
        user = CustomUser.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="password123",
        )
        # 実行：対象ユーザー詳細ページにアクセス
        url = reverse("accounts:user_detail", kwargs={"pk": user.pk})
        response = client.get(url)
        # 検証
        assert response.status_code == 200
        assert "accounts/user_detail.html" in [t.name for t in response.templates]
        assert response.context["user"].username == "alice"
        assert response.context["user"].email == "alice@example.com"
        assert response.context["user"].birthday is None
        assert response.context["user"].is_deleted is False

    def test_user_updated_at_changes_on_update(self, client):
        """ユーザー情報を更新した際、更新されることを確認"""
        user = CustomUser.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="password123",
        )
        old_updated_at = user.updated_at

        before_update = timezone.now()
        user.username = "bobby"
        user.save()

        user.refresh_from_db()
        assert user.updated_at > old_updated_at
        assert user.updated_at > before_update

    def test_user_is_deleted_flag_after_delete(self, client):
        """削除処理後、削除済みになることを確認"""
        user = CustomUser.objects.create_user(
            username="charlie",
            email="charlie@example.com",
            password="password123",
        )
        delete_url = reverse("accounts:user_delete", kwargs={"pk": user.pk})
        response = client.post(delete_url, follow=True)
        user.refresh_from_db()

        assert response.status_code == 200
        assert user.is_deleted is True

    def test_edit_link_redirects_to_edit_view(self, client):
        """「編集」リンク押下で編集画面に遷移することを確認"""
        user = CustomUser.objects.create_user(
            username="daisy",
            email="daisy@example.com",
            password="password123",
        )
        detail_url = reverse("accounts:user_detail", kwargs={"pk": user.pk})
        response = client.get(detail_url)
        assert response.status_code == 200

        edit_url = reverse("accounts:user_edit", kwargs={"pk": user.pk})
        # ページ内リンクが正しいURLを含むことを確認（テンプレートHTML内）
        assert edit_url in response.content.decode()

        # 実際にアクセスして遷移を確認
        edit_response = client.get(edit_url)
        assert edit_response.status_code == 200
        assert "accounts/user_edit.html" in [t.name for t in edit_response.templates]

    def test_delete_link_redirects_to_delete_view(self, client):
        """「削除」リンク押下で削除画面に遷移することを確認"""
        user = CustomUser.objects.create_user(
            username="eric",
            email="eric@example.com",
            password="password123",
        )
        detail_url = reverse("accounts:user_detail", kwargs={"pk": user.pk})
        response = client.get(detail_url)
        assert response.status_code == 200

        delete_url = reverse("accounts:user_delete", kwargs={"pk": user.pk})
        assert delete_url in response.content.decode()

        delete_page = client.get(delete_url)
        assert delete_page.status_code == 200
        assert "accounts/user_delete.html" in [t.name for t in delete_page.templates]

    def test_back_to_list_link_redirects_to_user_list(self, client):
        """「ユーザー一覧に戻る」リンク押下で一覧ページに遷移することを確認"""
        user = CustomUser.objects.create_user(
            username="frank",
            email="frank@example.com",
            password="password123",
        )
        detail_url = reverse("accounts:user_detail", kwargs={"pk": user.pk})
        response = client.get(detail_url)
        assert response.status_code == 200

        list_url = reverse("accounts:user_list")
        assert list_url in response.content.decode()

        list_response = client.get(list_url)
        assert list_response.status_code == 200
        assert "accounts/user_list.html" in [t.name for t in list_response.templates]
