from bookshelf_app.tools.cache import book_search as target


class FakeResult:
    rowcount = 2


class FakeSession:
    committed = False
    statement = None

    def execute(self, stmt):
        self.statement = stmt
        return FakeResult()

    def commit(self):
        self.committed = True


def test_clear_book_metadata_cache_deletes_all(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(target, "get_session", lambda: iter([session]))

    actual = target.clear_book_metadata_cache()

    assert actual == 2
    assert session.committed


def test_clear_book_metadata_cache_deletes_one_isbn(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(target, "get_session", lambda: iter([session]))

    actual = target.clear_book_metadata_cache("978-4-8144-0170-3")

    assert actual == 2
    assert session.committed


def test_clear_publisher_catalog_cache_deletes_all(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(target, "get_session", lambda: iter([session]))

    actual = target.clear_publisher_catalog_cache()

    assert actual == 2
    assert session.committed
