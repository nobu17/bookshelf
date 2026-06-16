# pylint: disable=unused-argument

import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.db.database import truncate_tables
from tests.integration.helper import (
    assert_book_response,
    auth_as_admin,
    auth_as_user,
    auth_headers,
    create_book,
    create_initial_accounts,
    create_review,
    create_tags,
    default_book_request,
    get_book_by_id,
    get_books_by_isbn13,
    update_book,
    update_book_tags,
)

client = TestClient(main.app)

URL_BASE = "/api/books"
URL_ISBN13 = URL_BASE + "/isbn13"
URL_BOOK_ID = URL_BASE + "/book_id"
URL_TAGS = URL_BASE + "/tags"


@pytest.fixture(scope="function", autouse=True)
def scope_function():
    yield


@pytest.fixture(scope="class", autouse=True)
def scope_class():
    create_initial_accounts()
    yield
    truncate_tables()


def test_books_list_isb13_incorrect_isbn(database_service):
    response = client.get(URL_ISBN13 + "/1234")
    # initial empty
    assert response.status_code == 422


def test_books_list_isb13_not_exists(database_service):
    response = client.get(URL_ISBN13 + "/9784814400690")
    # initial empty
    assert response.status_code == 404


def test_books_get_by_book_id_invalid_id(database_service):
    response = client.get(URL_BOOK_ID + "/invalid-book-id")

    assert response.status_code == 422


def test_books_get_by_book_id_not_exists(database_service):
    response = client.get(URL_BOOK_ID + "/50f65802-a5db-43cf-9dfc-3d5aea11d5dc")

    assert response.status_code == 404


def test_books_create_no_authorized(database_service):
    # post item with no token
    post_response1 = client.post(url=URL_BASE, json=default_book_request(image_url="https://example.com/cover.jpg"))
    assert post_response1.status_code == 401


@pytest.mark.parametrize(
    ["body"],
    [
        pytest.param(default_book_request(isbn13="1234"), id="invalid isbn13"),
        pytest.param(default_book_request(title=""), id="empty title"),
        pytest.param(default_book_request(title="x" * 101), id="too long title"),
        pytest.param(default_book_request(publisher=""), id="empty publisher"),
        pytest.param(default_book_request(authors=[]), id="empty authors"),
        pytest.param(default_book_request(image_url="x" * 1001), id="too long image url"),
    ],
)
def test_books_create_unprocessable(database_service, body: dict):
    token = auth_as_user(client)

    response = client.post(url=URL_BASE, json=body, headers=auth_headers(token))

    assert response.status_code == 422


def test_books_create_and_get(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    request_json = default_book_request(image_url="https://example.com/cover.jpg")
    # case1: post item as new
    post_json1 = create_book(client, token, image_url="https://example.com/cover.jpg")

    # confirm can get from isbn13
    books = get_books_by_isbn13(client, post_json1["isbn13"])
    assert len(books) == 1
    book1 = books[0]
    book1_id = book1["book_id"]
    assert_book_response(book1, request_json)

    # confirm can get from book_id
    book1 = get_book_by_id(client, book1_id)
    assert_book_response(book1, request_json)

    # case2: post same data again
    post_response2 = client.post(url=URL_BASE, json=request_json, headers=auth_headers(token))
    # response should be error
    assert post_response2.status_code == 422


def test_books_create_defaults_image_url_to_empty(database_service):
    token = auth_as_user(client)

    book = create_book(client, token)

    assert book["image_url"] == ""


def test_books_create_same_isbn(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    request_json1 = default_book_request()
    # precondition: post item as new
    create_book(client, token)

    # create same isbn item with other year publish date
    request_json2 = default_book_request(
        title="入門 継続的デリバリー(2)",
        authors=["著者1", "著者2", "著者3"],
        published_at="2024-01-10",
    )

    post_response1 = client.post(url=URL_BASE, json=request_json2, headers=auth_headers(token))
    assert post_response1.status_code == 200

    # confirm can get from isbn13
    books = get_books_by_isbn13(client, "9784814400690")
    # at first assert id exists
    assert len(books) == 2
    book1_id = books[0]["book_id"]
    assert book1_id is not None

    book2_id = books[1]["book_id"]
    assert book2_id is not None
    assert book1_id != book2_id

    # match the data by title due to not ensure the order
    if books[0]["title"] == "入門 継続的デリバリー":
        book1 = books[0]
        book2 = books[1]
    elif books[0]["title"] == "入門 継続的デリバリー(2)":
        book2 = books[0]
        book1 = books[1]
    else:
        raise ValueError("not expected book response.")

    assert_book_response(book1, request_json1)
    assert_book_response(book2, request_json2)


def test_books_search_masters_as_admin(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    book1 = create_book(client, user_token)
    book2 = create_book(
        client,
        user_token,
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        publisher="オライリージャパン",
        authors=["著者A"],
        published_at="2024-01-10",
    )
    create_review(client, user_token, book1["book_id"])
    create_review(client, user_token, book1["book_id"], state=2, completed_at="2024-01-10T00:00:00+09:00")

    response = client.get(url=URL_BASE, headers=auth_headers(admin_token))

    assert response.status_code == 200
    books = response.json()["books"]
    assert {book["book_id"] for book in books} == {book1["book_id"], book2["book_id"]}
    book1_response = next(book for book in books if book["book_id"] == book1["book_id"])
    book2_response = next(book for book in books if book["book_id"] == book2["book_id"])
    assert book1_response["review_count"] == 2
    assert book2_response["review_count"] == 0


def test_books_search_masters_filters_by_keyword(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    create_book(client, user_token)
    target = create_book(
        client,
        user_token,
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        publisher="オライリージャパン",
        authors=["著者A"],
        published_at="2024-01-10",
    )

    response = client.get(url=URL_BASE + "?keyword=著者A", headers=auth_headers(admin_token))

    assert response.status_code == 200
    books = response.json()["books"]
    assert len(books) == 1
    assert books[0]["book_id"] == target["book_id"]


@pytest.mark.parametrize(
    ["keyword", "target_overrides"],
    [
        pytest.param(
            "architecture-notes-title-keyword",
            {
                "isbn13": "9784798178417",
                "title": "architecture-notes-title-keyword",
                "publisher": "Tech Publisher Title Search",
                "authors": ["Author Title Search"],
                "published_at": "2025-01-10",
            },
            id="title",
        ),
        pytest.param(
            "9784297137830",
            {
                "isbn13": "9784297137830",
                "title": "Database Search Notes",
                "publisher": "Tech Publisher Isbn Search",
                "authors": ["Author Isbn Search"],
                "published_at": "2025-01-11",
            },
            id="isbn13",
        ),
        pytest.param(
            "publisher-field-keyword",
            {
                "isbn13": "9784798178424",
                "title": "Publisher Search Notes",
                "publisher": "publisher-field-keyword",
                "authors": ["Author Publisher Search"],
                "published_at": "2025-01-12",
            },
            id="publisher",
        ),
        pytest.param(
            "author-field-keyword",
            {
                "isbn13": "9784798178431",
                "title": "Author Search Notes",
                "publisher": "Tech Publisher Author Search",
                "authors": ["author-field-keyword"],
                "published_at": "2025-01-13",
            },
            id="author",
        ),
    ],
)
def test_books_search_masters_filters_by_each_keyword_field(database_service, keyword: str, target_overrides: dict):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    target = create_book(client, user_token, **target_overrides)

    response = client.get(url=URL_BASE + f"?keyword={keyword}", headers=auth_headers(admin_token))

    assert response.status_code == 200
    books = response.json()["books"]
    assert [book["book_id"] for book in books] == [target["book_id"]]


def test_books_search_masters_filters_case_insensitively(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    target = create_book(
        client,
        user_token,
        isbn13="9784798178448",
        title="CASE-INSENSITIVE-BOOK-SEARCH",
        publisher="Tech Publisher Case Search",
        authors=["Author Case Search"],
        published_at="2025-01-14",
    )

    response = client.get(url=URL_BASE + "?keyword=case-insensitive-book-search", headers=auth_headers(admin_token))

    assert response.status_code == 200
    books = response.json()["books"]
    assert [book["book_id"] for book in books] == [target["book_id"]]


def test_books_search_masters_no_authorization(database_service):
    response = client.get(url=URL_BASE)

    assert response.status_code == 401


def test_books_search_masters_denied_as_user(database_service):
    token = auth_as_user(client)

    response = client.get(url=URL_BASE, headers=auth_headers(token))

    assert response.status_code == 403


def test_books_update_master_by_book_id(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    book_id = create_book(client, user_token, image_url="https://example.com/original.jpg")["book_id"]
    tag_ids = create_tags(client, user_token)
    update_book_tags(client, user_token, book_id, tag_ids)

    request_json = default_book_request(
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        publisher="オライリージャパン",
        authors=["著者A", "著者B"],
        published_at="2024-01-10",
        image_url="https://example.com/updated.jpg",
    )

    updated = update_book(client, admin_token, book_id, **request_json)

    assert_book_response(updated, request_json)
    assert {tag["name"] for tag in updated["tags"]} == {"Tag1", "Tag2", "Tag3"}
    assert_tag_ids(updated["tags"], tag_ids)
    assert_book_response(get_book_by_id(client, book_id), request_json)
    assert_tag_ids(get_book_by_id(client, book_id)["tags"], tag_ids)


def test_books_update_master_no_authorization(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    response = client.put(url=URL_BASE + "/" + book_id, json=default_book_request(title="更新"))

    assert response.status_code == 401


def test_books_update_master_denied_as_user(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    response = client.put(
        url=URL_BASE + "/" + book_id,
        json=default_book_request(title="更新"),
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_books_update_master_not_exists(database_service):
    admin_token = auth_as_admin(client)
    not_existed_book_id = "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"

    response = client.put(
        url=URL_BASE + "/" + not_existed_book_id,
        json=default_book_request(title="更新"),
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 404


def test_books_update_master_allows_same_isbn_and_same_year_as_another_book(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    book1 = create_book(client, user_token)
    book2 = create_book(
        client,
        user_token,
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        authors=["著者A"],
        published_at="2024-01-10",
    )

    request_json = default_book_request(title="別レコードだが同じISBN年")

    updated = update_book(client, admin_token, book2["book_id"], **request_json)

    assert updated["book_id"] == book2["book_id"]
    assert updated["book_id"] != book1["book_id"]
    assert_book_response(updated, request_json)


@pytest.mark.parametrize(
    ["body"],
    [
        pytest.param(default_book_request(isbn13="1234"), id="invalid isbn13"),
        pytest.param(default_book_request(title=""), id="empty title"),
        pytest.param(default_book_request(title="x" * 101), id="too long title"),
        pytest.param(default_book_request(publisher=""), id="empty publisher"),
        pytest.param(default_book_request(authors=[]), id="empty authors"),
        pytest.param(default_book_request(image_url="x" * 1001), id="too long image url"),
    ],
)
def test_books_update_master_unprocessable(database_service, body: dict):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    book_id = create_book(client, user_token)["book_id"]

    response = client.put(url=URL_BASE + "/" + book_id, json=body, headers=auth_headers(admin_token))

    assert response.status_code == 422


def test_books_update_tags(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # creating tags as pre condition
    tag_ids = create_tags(client, token)

    # post item as new as pre condition
    book1_id = create_book(client, token)["book_id"]

    # case1: add tags from 0 tags
    update_book_tags(client, token, book1_id, tag_ids)

    # confirm by get from book_id
    book1 = get_book_by_id(client, book1_id)
    tags = book1["tags"]
    assert len(tags) == 3
    assert_tag_ids(tags, tag_ids)

    # case2: remove tags (2 items)
    update_book_tags(client, token, book1_id, [tag_ids[0], tag_ids[2]])

    # confirm by get from book_id
    book1 = get_book_by_id(client, book1_id)
    tags = book1["tags"]
    assert len(tags) == 2
    assert_tag_ids(tags, [tag_ids[0], tag_ids[2]])

    # case3: add tag
    update_book_tags(client, token, book1_id, tag_ids)

    # confirm by get from book_id
    book1 = get_book_by_id(client, book1_id)
    tags = book1["tags"]
    assert len(tags) == 3
    assert_tag_ids(tags, tag_ids)

    # case4: remove all
    update_book_tags(client, token, book1_id, [])

    # confirm by get from book_id
    book1 = get_book_by_id(client, book1_id)
    tags = book1["tags"]
    assert len(tags) == 0


def assert_tag_ids(tags: list[dict], expected_tag_ids: list[str]) -> None:
    assert {tag["tag_id"] for tag in tags} == set(expected_tag_ids)


def test_books_update_tags_no_authorization(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]
    tag_ids = create_tags(client, token)

    response = client.put(url=URL_TAGS + "/" + book_id, json={"tag_ids": tag_ids})

    assert response.status_code == 401


def test_books_update_tags_book_not_exists(database_service):
    token = auth_as_user(client)
    tag_ids = create_tags(client, token)
    not_existed_book_id = "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"

    response = client.put(
        url=URL_TAGS + "/" + not_existed_book_id,
        json={"tag_ids": tag_ids},
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_books_update_tags_tag_not_exists(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    response = client.put(
        url=URL_TAGS + "/" + book_id,
        json={"tag_ids": ["50f65802-a5db-43cf-9dfc-3d5aea11d5dc"]},
        headers=auth_headers(token),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    ["body"],
    [
        pytest.param({"tag_ids": ["invalid-tag-id"]}, id="invalid tag id"),
        pytest.param({"tag_ids": []}, id="invalid path book id"),
    ],
)
def test_books_update_tags_unprocessable(database_service, body: dict):
    token = auth_as_user(client)
    book_id = "invalid-book-id" if body["tag_ids"] == [] else "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"

    response = client.put(url=URL_TAGS + "/" + book_id, json=body, headers=auth_headers(token))

    assert response.status_code == 422


def test_books_update_tags_rejects_legacy_body_book_id(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]
    other_book_id = create_book(
        client,
        token,
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        authors=["著者A"],
        published_at="2024-01-10",
    )["book_id"]
    tag_ids = create_tags(client, token)

    response = client.put(
        url=URL_TAGS + "/" + book_id,
        json={"book_id": other_book_id, "tag_ids": tag_ids},
        headers=auth_headers(token),
    )

    assert response.status_code == 422
    assert get_book_by_id(client, book_id)["tags"] == []
    assert get_book_by_id(client, other_book_id)["tags"] == []
