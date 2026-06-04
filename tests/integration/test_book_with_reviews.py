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
    create_review,
    create_initial_accounts,
    create_tags,
    default_book_request,
    get_user_id,
    update_book_tags,
)

client = TestClient(main.app)

URL_WITH_REVIEW_BASE = "/api/book_with_reviews"
URL_WITH_REVIEW = URL_WITH_REVIEW_BASE + "/user_id"
URL_WITH_REVIEW_ME = URL_WITH_REVIEW_BASE + "/me"
URL_WITH_REVIEW_LATEST = URL_WITH_REVIEW_BASE + "/latest"
URL_WITH_REVIEW_FOR_EDIT_ME = URL_WITH_REVIEW_BASE + "/for_edit/me"
URL_WITH_REVIEW_FOR_EDIT_BOOK_ID = URL_WITH_REVIEW_BASE + "/for_edit/book_id"


@pytest.fixture(scope="function", autouse=True)
def scope_function():
    yield


@pytest.fixture(scope="class", autouse=True)
def scope_class():
    create_initial_accounts()
    yield
    truncate_tables()


def test_books_list_with_reviews(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # creating tags as pre condition
    tag_ids = create_tags(client, token)

    request_json = default_book_request(image_url="https://example.com/cover.jpg")
    # post item as new as pre condition
    book1_id = create_book(client, token, image_url="https://example.com/cover.jpg")["book_id"]

    # add tags as precondition
    update_book_tags(client, token, book1_id, tag_ids)

    # add reviews as precondition
    create_review(client, token, book1_id)

    user_id = get_user_id(client, token)
    cases = [
        (URL_WITH_REVIEW_ME, auth_headers(token)),
        (URL_WITH_REVIEW + "/" + user_id, auth_headers(token)),
        (URL_WITH_REVIEW_LATEST + "/100", {}),
        (URL_WITH_REVIEW_FOR_EDIT_ME, auth_headers(token)),
    ]
    for url, headers in cases:
        response = client.get(url, headers=headers)
        assert response.status_code == 200
        _assert_books_with_reviews_response(response.json(), request_json)

    response = client.get(URL_WITH_REVIEW_FOR_EDIT_BOOK_ID + "/" + book1_id, headers=auth_headers(token))
    assert response.status_code == 200
    assert_book_response(response.json(), request_json)


def test_book_with_reviews_public_endpoints_exclude_draft_and_for_edit_includes_it(database_service):
    token = auth_as_user(client)
    request_json = default_book_request(image_url="https://example.com/cover.jpg")
    book_id = create_book(client, token, image_url="https://example.com/cover.jpg")["book_id"]
    create_review(client, token, book_id, content="draft review", is_draft=True)

    response = client.get(URL_WITH_REVIEW_ME, headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json() == {"books_with_reviews": []}

    response = client.get(URL_WITH_REVIEW_LATEST + "/100")
    assert response.status_code == 200
    assert response.json() == {"books_with_reviews": []}

    response = client.get(URL_WITH_REVIEW_FOR_EDIT_ME, headers=auth_headers(token))
    assert response.status_code == 200
    _assert_books_with_reviews_response(response.json(), request_json)
    assert response.json()["books_with_reviews"][0]["reviews"][0]["is_draft"] is True

    response = client.get(URL_WITH_REVIEW_FOR_EDIT_BOOK_ID + "/" + book_id, headers=auth_headers(token))
    assert response.status_code == 200
    assert_book_response(response.json(), request_json)
    assert response.json()["reviews"][0]["is_draft"] is True


def test_book_with_reviews_for_edit_book_id_includes_only_my_reviews(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    request_json = default_book_request(
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        authors=["著者A"],
        published_at="2024-01-10",
    )
    book_id = create_book(
        client,
        user_token,
        isbn13="9784814400973",
        title="クリーンコードクックブック",
        authors=["著者A"],
        published_at="2024-01-10",
    )["book_id"]
    user_review = create_review(client, user_token, book_id, content="user review")
    create_review(client, admin_token, book_id, content="admin review")

    response = client.get(URL_WITH_REVIEW_FOR_EDIT_BOOK_ID + "/" + book_id, headers=auth_headers(user_token))

    assert response.status_code == 200
    assert_book_response(response.json(), request_json)
    assert [review["review_id"] for review in response.json()["reviews"]] == [user_review["review_id"]]


def test_book_with_reviews_me_does_not_include_other_user_reviews(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    user_book = create_book(
        client,
        user_token,
        isbn13="9784297143176",
        title="[入門]ドメイン駆動設計",
        authors=["著者B"],
        published_at="2024-07-01",
    )
    create_review(client, user_token, user_book["book_id"], content="user review")
    admin_book = create_book(
        client,
        admin_token,
        isbn13="9784798121963",
        title="エリック・エヴァンスのドメイン駆動設計",
        authors=["著者C"],
        published_at="2011-04-01",
    )
    create_review(client, admin_token, admin_book["book_id"], content="admin review")

    response = client.get(URL_WITH_REVIEW_ME, headers=auth_headers(user_token))

    assert response.status_code == 200
    books = response.json()["books_with_reviews"]
    assert [book["book_id"] for book in books] == [user_book["book_id"]]


def _assert_books_with_reviews_response(body: dict, expected_book: dict) -> None:
    assert len(body["books_with_reviews"]) == 1
    assert_book_response(body["books_with_reviews"][0], expected_book)
