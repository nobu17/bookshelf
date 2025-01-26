# pylint: disable=unused-argument

import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.db.database import truncate_tables
from tests.integration.helper import auth_as_user, create_initial_accounts, get_user_id

client = TestClient(main.app)

URL_BASE = "/api/books"
URL_ISBN13 = URL_BASE + "/isbn13"
URL_BOOK_ID = URL_BASE + "/book_id"
URL_TAGS = URL_BASE + "/tags"

URL_WITH_REVIEW = URL_BASE + "/reviews/user_id"
URL_WITH_REVIEW_ME = URL_BASE + "/reviews/me"
URL_REVIEW_BASE = "/api/reviews"


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
    request_json = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
    }
    # post item with no token
    post_response1 = client.post(url=URL_BASE, json=request_json)
    assert post_response1.status_code == 401


def test_books_create_and_get(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    request_json = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
    }
    # case1: post item as new
    post_response1 = client.post(url=URL_BASE, json=request_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()

    # confirm can get from isbn13
    get_response1 = client.get(URL_ISBN13 + "/" + post_json1["isbn13"])
    assert get_response1.status_code == 200
    get_json1 = get_response1.json()
    assert len(get_json1["books"]) == 1
    book1 = get_json1["books"][0]
    book1_id = book1["book_id"]
    assert book1_id is not None
    assert book1["isbn13"] == "9784814400690"
    assert book1["title"] == "入門 継続的デリバリー"
    assert book1["publisher"] == "オライリージャパン"
    assert book1["published_at"] == "2023-01-10"
    assert book1["authors"][0] == "著者1"
    assert book1["authors"][1] == "著者2"

    # confirm can get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    book1_id = book1["book_id"]
    assert book1_id is not None
    assert book1["isbn13"] == "9784814400690"
    assert book1["title"] == "入門 継続的デリバリー"
    assert book1["publisher"] == "オライリージャパン"
    assert book1["published_at"] == "2023-01-10"
    assert book1["authors"][0] == "著者1"
    assert book1["authors"][1] == "著者2"

    # case2: post same data again
    post_response2 = client.post(url=URL_BASE, json=request_json, headers={"Authorization": "Bearer " + token})
    # response should be error
    assert post_response2.status_code == 422


def test_books_create_same_isbn(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    request_json1 = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
    }
    # precondition: post item as new
    post_response1 = client.post(url=URL_BASE, json=request_json1, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200

    # create same isbn item with other year publish date
    request_json2 = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー(2)",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2", "著者3"],
        "published_at": "2024-01-10",
    }

    post_response1 = client.post(url=URL_BASE, json=request_json2, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200

    # confirm can get from isbn13
    get_response1 = client.get(URL_ISBN13 + "/" + "9784814400690")
    assert get_response1.status_code == 200
    get_json1 = get_response1.json()
    assert len(get_json1["books"]) == 2
    book1 = get_json1["books"][0]
    book1_id = book1["book_id"]
    assert book1_id is not None
    assert book1["isbn13"] == "9784814400690"
    assert book1["title"] == "入門 継続的デリバリー"
    assert book1["publisher"] == "オライリージャパン"
    assert book1["published_at"] == "2023-01-10"
    assert book1["authors"][0] == "著者1"
    assert book1["authors"][1] == "著者2"

    book2 = get_json1["books"][1]
    book2_id = book2["book_id"]
    assert book2_id is not None
    assert book2["isbn13"] == "9784814400690"
    assert book2["title"] == "入門 継続的デリバリー(2)"
    assert book2["publisher"] == "オライリージャパン"
    assert book2["published_at"] == "2024-01-10"
    assert book2["authors"][0] == "著者1"
    assert book2["authors"][1] == "著者2"
    assert book2["authors"][2] == "著者3"


def test_books_update_tags(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # creating tags as pre condition
    tag_ids = _create_tags(client, token)

    request_json = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
    }
    # post item as new as pre condition
    post_response1 = client.post(url=URL_BASE, json=request_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()
    book1_id = post_json1["book_id"]
    assert book1_id is not None

    # case1: add tags from 0 tags
    tag_req = {"book_id": book1_id, "tag_ids": tag_ids}
    put_response1 = client.put(
        url=URL_TAGS + "/" + book1_id, json=tag_req, headers={"Authorization": "Bearer " + token}
    )
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
    put_response1 = client.put(
        url=URL_TAGS + "/" + book1_id, json=tag_req, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    tags = book1["tags"]
    assert len(tags) == 2

    # case3: add tag
    tag_req = {"book_id": book1_id, "tag_ids": tag_ids}
    put_response1 = client.put(
        url=URL_TAGS + "/" + book1_id, json=tag_req, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    tags = book1["tags"]
    assert len(tags) == 3

    # case4: remove all
    tag_req = {"book_id": book1_id, "tag_ids": []}
    put_response1 = client.put(
        url=URL_TAGS + "/" + book1_id, json=tag_req, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm by get from book_id
    get_response1 = client.get(URL_BOOK_ID + "/" + book1_id)
    assert get_response1.status_code == 200
    book1 = get_response1.json()
    tags = book1["tags"]
    assert len(tags) == 0


# todo: error parameter case test


def test_books_list_with_reviews(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # creating tags as pre condition
    tag_ids = _create_tags(client, token)

    request_json = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
    }
    # post item as new as pre condition
    post_response1 = client.post(url=URL_BASE, json=request_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()
    book1_id = post_json1["book_id"]
    assert book1_id is not None

    # add tags as precondition
    tag_req = {"book_id": book1_id, "tag_ids": tag_ids}
    put_response1 = client.put(
        url=URL_TAGS + "/" + book1_id, json=tag_req, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # add reviews as precondition
    req_json = {
        "book_id": book1_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_REVIEW_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200

    # act1: get by my review
    response = client.get(URL_WITH_REVIEW_ME, headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    print(str(response.json()))

    # act2: get by umy ser id
    user_id = get_user_id(client, token)
    response = client.get(URL_WITH_REVIEW + "/" + user_id, headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    print(str(response.json()))


def _create_tags(t_client: TestClient, token: str) -> list[str]:
    tag_ids: list[str] = []
    url = "/api/tags"
    tag_req1 = {"name": "Tag1"}
    post_response = t_client.post(url=url, json=tag_req1, headers={"Authorization": "Bearer " + token})
    assert post_response.status_code == 200
    resp_json1 = post_response.json()
    tag_ids.append(str(resp_json1["tag_id"]))

    tag_req2 = {"name": "Tag2"}
    post_response = t_client.post(url=url, json=tag_req2, headers={"Authorization": "Bearer " + token})
    assert post_response.status_code == 200
    resp_json2 = post_response.json()
    tag_ids.append(str(resp_json2["tag_id"]))

    tag_req3 = {"name": "Tag3"}
    post_response = t_client.post(url=url, json=tag_req3, headers={"Authorization": "Bearer " + token})
    assert post_response.status_code == 200
    resp_json3 = post_response.json()
    tag_ids.append(str(resp_json3["tag_id"]))

    return tag_ids
