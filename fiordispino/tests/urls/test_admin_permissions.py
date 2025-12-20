import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from fiordispino.models import GamesToPlay, GamePlayed
from fiordispino.admin import GamesToPlayAdmin, GamePlayedAdmin


@pytest.mark.django_db
class TestAdminPermissions:
    """
    Test suite for Admin ModelAdmin permissions.
    These tests ensure that the custom logic for add, change, and delete
    is correctly applied in the Django Admin interface.
    """

    @pytest.fixture
    def admin_site(self):
        return AdminSite()

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_games_to_play_admin_permissions(self, admin_site, request_factory, admin_user):
        """
        Verify that GamesToPlayAdmin prevents adding/changing but allows deleting.
        """
        model_admin = GamesToPlayAdmin(GamesToPlay, admin_site)
        request = request_factory.get('/admin')
        request.user = admin_user

        # Test has_add_permission (uses forbid_add_permission)
        assert model_admin.has_add_permission(request) is False

        # Test has_change_permission (uses forbid_change_permission)
        assert model_admin.has_change_permission(request) is False

        # Test has_delete_permission (explicitly returns True)
        assert model_admin.has_delete_permission(request) is True

    def test_game_played_admin_permissions(self, admin_site, request_factory, admin_user):
        """
        Verify that GamePlayedAdmin prevents adding/changing but allows deleting.
        """
        model_admin = GamePlayedAdmin(GamePlayed, admin_site)
        request = request_factory.get('/admin')
        request.user = admin_user

        # Test has_add_permission
        assert model_admin.has_add_permission(request) is False

        # Test has_change_permission
        assert model_admin.has_change_permission(request) is False

        # Test has_delete_permission
        assert model_admin.has_delete_permission(request) is True