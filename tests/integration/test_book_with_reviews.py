# pylint: disable=unused-argument

import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.db.database import truncate_tables
from tests.integration.helper import (
    assert_book_response,
    auth_as_user,
    auth_headers,
    create_book,
    create_initial_accounts,
    create_tags,
    default_book_request,
    get_user_id,
)

client = TestClient(main.app)

URL_BASE = "/api/books"
URL_ISBN13 = URL_BASE + "/isbn13"
URL_BOOK_ID = URL_BASE + "/book_id"
URL_TAGS = URL_BASE + "/tags"
URL_REVIEW_BASE = "/api/reviews"

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
    tag_req = {"book_id": book1_id, "tag_ids": tag_ids}
    put_response1 = client.put(url=URL_TAGS + "/" + book1_id, json=tag_req, headers=auth_headers(token))
    assert put_response1.status_code == 200

    # add reviews as precondition
    req_json = {
        "book_id": book1_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_REVIEW_BASE, json=req_json, headers=auth_headers(token))
    assert post_response1.status_code == 200

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


def _assert_books_with_reviews_response(body: dict, expected_book: dict) -> None:
    assert len(body["books_with_reviews"]) == 1
    assert_book_response(body["books_with_reviews"][0], expected_book)
