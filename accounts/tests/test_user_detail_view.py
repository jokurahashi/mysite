import pytest
from django.urls import reverse
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
