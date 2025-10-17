import pytest
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser


@pytest.mark.django_db
class TestUserListView:

    url = reverse("accounts:user_list")

    @pytest.fixture
    def create_users(self):
        """テスト用ユーザーを作成"""
        base_time = timezone.now()
        u1 = CustomUser.objects.create(
            username="Alice",
            email="alice@example.com",
            updated_at=base_time,
            created_at=base_time,
        )
        u2 = CustomUser.objects.create(
            username="Bob",
            email="bob@example.com",
            updated_at=base_time + timezone.timedelta(seconds=10),
            created_at=base_time + timezone.timedelta(seconds=10),
        )
        u3 = CustomUser.objects.create(
            username="Charlie",
            email="charlie@SAMPLE.com",
            updated_at=base_time + timezone.timedelta(seconds=20),
            created_at=base_time + timezone.timedelta(seconds=20),
        )
        return [u1, u2, u3]

    def test_user_list_all_users_displayed(self, client, create_users):
        """全ユーザーが一覧に表示されること"""

        response = client.get(self.url)

        users = response.context["users"]

        # 並び順が更新日時、作成日時の降順であること
        sorted_users = sorted(
            create_users, key=lambda u: (u.updated_at, u.created_at), reverse=True
        )

        assert response.status_code == 200
        assert "accounts/user_list.html" in [t.name for t in response.templates]
        assert len(users) == 3
        assert list(users) == sorted_users

    def test_user_list_filter_by_username_exact_match(self, client, create_users):
        """usernameを部分一致検索で取得できること(大文字小文字区別あり)"""

        response = client.get(self.url, {"username": "Ali"})
        users = response.context["users"]

        assert response.status_code == 200
        assert len(users) == 1
        assert users[0].username == "Alice"

    def test_user_list_filter_by_email_case_insensitive(self, client, create_users):
        """emailを大文字小文字区別せず部分一致検索できること"""

        response = client.get(self.url, {"email": "sample.com"})

        users = response.context["users"]

        assert response.status_code == 200
        assert len(users) == 1
        assert users[0].email == "charlie@SAMPLE.com"

    def test_user_list_filter_combined(self, client, create_users):
        """usernameとemail両方指定した場合、両条件に一致するもののみ返す"""

        response = client.get(self.url, {"username": "Bob", "email": "example.com"})
        users = response.context["users"]

        assert response.status_code == 200
        assert len(users) == 1
        assert users[0].username == "Bob"

    def test_user_list_empty_result(self, client, create_users):
        """条件に一致しない場合、空のリストになること"""

        response = client.get(self.url, {"username": "Zoe"})
        users = response.context["users"]
        assert len(users) == 0
