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


def test_books_create_no_authorized(database_service):
    # post item with no token
    post_response1 = client.post(url=URL_BASE, json=default_book_request(image_url="https://example.com/cover.jpg"))
    assert post_response1.status_code == 401


def test_books_create_and_get(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    request_json = default_book_request(image_url="https://example.com/cover.jpg")
    # case1: post item as new
    post_response1 = client.post(url=URL_BASE, json=request_json, headers=auth_headers(token))
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()

    # confirm can get from isbn13
    get_response1 = client.get(URL_ISBN13 + "/" + post_json1["isbn13"])
    assert get_response1.status_code == 200
    get_json1 = get_response1.json()
    assert len(get_json1["books"]) == 1
    book1 = get_json1["books"][0]
    book1_id = book1["book_id"]
    assert_book_response(book1, request_json)

    # confirm can get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    assert_book_response(book1, request_json)

    # case2: post same data again
    post_response2 = client.post(url=URL_BASE, json=request_json, headers=auth_headers(token))
    # response should be error
    assert post_response2.status_code == 422


def test_books_create_defaults_image_url_to_empty(database_service):
    token = auth_as_user(client)

    book = create_book(client, token)

    assert book["image_url"] == ""


def test_books_create_rejects_too_long_image_url(database_service):
    token = auth_as_user(client)

    response = client.post(
        url=URL_BASE,
        json=default_book_request(image_url="x" * 1001),
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_books_create_same_isbn(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    request_json1 = default_book_request()
    # precondition: post item as new
    post_response1 = client.post(url=URL_BASE, json=request_json1, headers=auth_headers(token))
    assert post_response1.status_code == 200

    # create same isbn item with other year publish date
    request_json2 = default_book_request(
        title="入門 継続的デリバリー(2)",
        authors=["著者1", "著者2", "著者3"],
        published_at="2024-01-10",
    )

    post_response1 = client.post(url=URL_BASE, json=request_json2, headers=auth_headers(token))
    assert post_response1.status_code == 200

    # confirm can get from isbn13
    get_response1 = client.get(URL_ISBN13 + "/" + "9784814400690")
    assert get_response1.status_code == 200
    get_json1 = get_response1.json()
    # at first assert id exists
    assert len(get_json1["books"]) == 2
    book1_id = get_json1["books"][0]["book_id"]
    assert book1_id is not None

    book2_id = get_json1["books"][1]["book_id"]
    assert book2_id is not None
    assert book1_id is not book2_id

    # match the data by title due to not ensure the order
    if get_json1["books"][0]["title"] == "入門 継続的デリバリー":
        book1 = get_json1["books"][0]
        book2 = get_json1["books"][1]
    elif get_json1["books"][0]["title"] == "入門 継続的デリバリー(2)":
        book2 = get_json1["books"][0]
        book1 = get_json1["books"][1]
    else:
        raise ValueError("not expected book response.")

    assert_book_response(book1, request_json1)
    assert_book_response(book2, request_json2)


def test_books_update_tags(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # creating tags as pre condition
    tag_ids = create_tags(client, token)

    # post item as new as pre condition
    book1_id = create_book(client, token)["book_id"]

    # case1: add tags from 0 tags
    tag_req = {"book_id": book1_id, "tag_ids": tag_ids}
    put_response1 = client.put(url=URL_TAGS + "/" + book1_id, json=tag_req, headers=auth_headers(token))
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    print(book1)
    tags = book1["tags"]
    assert len(tags) == 3

    # case2: remove tags (2 items)
    tag_req = {"book_id": book1_id, "tag_ids": [tag_ids[0], tag_ids[2]]}
    put_response1 = client.put(url=URL_TAGS + "/" + book1_id, json=tag_req, headers=auth_headers(token))
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    tags = book1["tags"]
    assert len(tags) == 2

    # case3: add tag
    tag_req = {"book_id": book1_id, "tag_ids": tag_ids}
    put_response1 = client.put(url=URL_TAGS + "/" + book1_id, json=tag_req, headers=auth_headers(token))
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    tags = book1["tags"]
    assert len(tags) == 3

    # case4: remove all
    tag_req = {"book_id": book1_id, "tag_ids": []}
    put_response1 = client.put(url=URL_TAGS + "/" + book1_id, json=tag_req, headers=auth_headers(token))
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    tags = book1["tags"]
    assert len(tags) == 0


# todo: error parameter case test
