from types import SimpleNamespace

from bookshelf_app.api.auth.domain import Email
from bookshelf_app.tools.seeds import user as seed_user


class FakeCryptService:
    def create_hash(self, _password):
        return "hashed-password"


def test_ensure_initial_admin_creates_admin_when_missing(monkeypatch):
    store = {}

    monkeypatch.setattr(seed_user, "get_tool_settings", lambda: _settings())
    monkeypatch.setattr(seed_user, "get_session", lambda: iter([object()]))
    monkeypatch.setattr(seed_user, "SqlUserRepository", _repo_factory(store))
    monkeypatch.setattr(seed_user, "CryptService", FakeCryptService)

    result = seed_user.ensure_initial_admin()

    assert result.created is True
    assert result.user.name.value == "admin"
    assert result.user.email.value == "admin@example.com"
    assert [str(role) for role in result.user.roles] == ["admin"]
    assert list(store.keys()) == ["admin@example.com"]


def test_ensure_initial_admin_returns_existing_admin_when_email_exists(monkeypatch):
    store = {}

    monkeypatch.setattr(seed_user, "get_tool_settings", lambda: _settings())
    monkeypatch.setattr(seed_user, "get_session", lambda: iter([object()]))
    monkeypatch.setattr(seed_user, "SqlUserRepository", _repo_factory(store))
    monkeypatch.setattr(seed_user, "CryptService", FakeCryptService)

    created = seed_user.ensure_initial_admin()
    existing = seed_user.ensure_initial_admin()

    assert created.created is True
    assert existing.created is False
    assert existing.user.user_id == created.user.user_id
    assert len(store) == 1


def _settings():
    return SimpleNamespace(
        tool_initial_user_name="admin",
        tool_initial_user_mail="admin@example.com",
        tool_initial_user_pass="Abc12345",
    )


def _repo_factory(store):
    class FakeUserRepository:
        def __init__(self, _session):
            pass

        def find_by_email(self, email: Email):
            return store.get(email.value)

        def create(self, user):
            store[user.email.value] = user
            return user

    return FakeUserRepository
