from bookshelf_app.api.health import router as target


def test_health_returns_ok():
    response = target.health()

    assert response.status == "ok"


def test_health_db_executes_select(monkeypatch):
    statements: list[str] = []

    class FakeSession:
        def execute(self, statement):
            statements.append(str(statement))

    monkeypatch.setattr(target, "get_session", lambda: iter([FakeSession()]))

    response = target.health_db()

    assert response.status == "ok"
    assert statements == ["SELECT 1"]
