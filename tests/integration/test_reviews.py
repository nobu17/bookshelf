# pylint: disable=unused-argument

import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.db.database import truncate_table, truncate_tables
from tests.integration.helper import auth_as_user, create_initial_accounts

client = TestClient(main.app)

URL_BASE = "/api/reviews"


@pytest.fixture(scope="class", autouse=True)
def scope_class():
    create_initial_accounts()
    yield
    truncate_tables()


@pytest.fixture(scope="function", autouse=True)
def scope_function():
    yield
    truncate_table("book_reviews")


def test_review_get_by_id_not_exists(database_service):
    response = client.get(URL_BASE + "/find?review_id=" + "50f65802-a5db-43cf-9dfc-3d5aea11d5dc")
    # parameter id is not exists, so should return 404
    assert response.status_code == 404


def test_review_get_my_reviews_not_authorized(database_service):
    # no login
    response = client.get(URL_BASE + "/me")
    # return empty
    assert response.status_code == 401


def test_review_get_my_reviews_empty(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)

    response = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    # return empty
    assert response.status_code == 200
    assert response.json() == {"reviews": []}


def test_review_post_create_not_authorized(database_service):
    # prepare token for creating book data as initial
    token = auth_as_user(client)
    book_id = _create_initial_book(client, token)

    # case1: create new review
    req_json = {
        "book_id": book_id,
        "content": "",
        "is_draft": "false",
        "state": 0,
        "completed_at": "2032-04-23T10:20:30.400+02:30",
    }
    # send without authorization token
    post_response1 = client.post(url=URL_BASE, json=req_json)
    assert post_response1.status_code == 401


def test_review_post_create(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_ids = _create_initial_books(client, token)

    # case1: create with not yet
    req_json = {
        "book_id": book_ids[0],
        "content": "",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] is not None
    assert review1["book_id"] == book_ids[0]
    assert review1["content"] == ""
    assert review1["is_draft"] is False
    assert review1["state"] == 0
    assert review1["completed_at"] is None
    assert review1["last_modified_at"] is not None

    # case2: create with in progress
    req_json = {
        "book_id": book_ids[1],
        "content": "In prog",
        "is_draft": False,
        "state": 1,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 2
    review1 = reviews[1]
    assert review1["review_id"] is not None
    assert review1["book_id"] == book_ids[1]
    assert review1["content"] == "In prog"
    assert review1["is_draft"] is False
    assert review1["state"] == 1
    assert review1["completed_at"] is None
    assert review1["last_modified_at"] is not None

    # case3: create with completed
    req_json = {
        "book_id": book_ids[2],
        "content": "Good book.",
        "is_draft": False,
        "state": 2,
        "completed_at": "2024-12-12 10:05",
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 3
    review1 = reviews[2]
    print(review1)
    assert review1["review_id"] is not None
    assert review1["book_id"] == book_ids[2]
    assert review1["content"] == "Good book."
    assert review1["is_draft"] is False
    assert review1["state"] == 2
    assert review1["completed_at"] is not None
    assert review1["last_modified_at"] is not None


def test_review_post_create_same_book_review(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = _create_initial_book(client, token)

    # case1: create new review
    req_json = {
        "book_id": book_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] is not None
    assert review1["book_id"] == book_id
    assert review1["content"] == "this is my first review."
    assert review1["is_draft"] is False
    assert review1["state"] == 0
    assert review1["completed_at"] is None

    # case2: create additional review of same book
    req_json = {
        "book_id": book_id,
        "content": "this is my second review.",
        "is_draft": True,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 2
    review1 = reviews[1]
    assert review1["review_id"] is not None
    assert review1["book_id"] == book_id
    assert review1["content"] == "this is my second review."
    assert review1["is_draft"] is True
    assert review1["state"] == 0
    assert review1["completed_at"] is None


def test_review_put_update_not_existed_data(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)

    not_existed_review_id = "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"
    req_update = {
        "review_id": not_existed_review_id,
        "content": "not existed",
        "is_draft": True,
        "state": 0,
    }
    put_response1 = client.put(
        url=URL_BASE + "/" + not_existed_review_id, json=req_update, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 422


def test_review_put_no_authorization(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = _create_initial_book(client, token)

    # create new review as precondition
    req_json = {
        "book_id": book_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    review_id = post_response1.json()["review_id"]

    # try to update without token
    req_update = {
        "review_id": review_id,
        "content": "update a content",
        "is_draft": True,
        "state": 0,
    }
    put_response1 = client.put(url=URL_BASE + "/" + review_id, json=req_update)
    assert put_response1.status_code == 401


def test_review_put_update(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = _create_initial_book(client, token)

    # create new review as precondition
    req_json = {
        "book_id": book_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    review_id = post_response1.json()["review_id"]

    # case1: update content and draft
    req_update = {
        "review_id": review_id,
        "content": "update a content",
        "is_draft": True,
        "state": 0,
    }
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id, json=req_update, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert review1["content"] == "update a content"
    assert review1["is_draft"] is True
    assert review1["state"] == 0
    assert review1["completed_at"] is None

    # case2: update state not yet to in-progress
    req_update = {
        "review_id": review_id,
        "content": "update a content",
        "is_draft": True,
        "state": 1,
    }
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id, json=req_update, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert review1["content"] == "update a content"
    assert review1["is_draft"] is True
    assert review1["state"] == 1
    assert review1["completed_at"] is None

    # case3: update in-progress to completed
    req_update = {
        "review_id": review_id,
        "content": "update a content",
        "is_draft": True,
        "state": 2,
        "completed_at": "2032-04-23T10:20:30.400+02:30",
    }
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id, json=req_update, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert review1["content"] == "update a content"
    assert review1["is_draft"] is True
    assert review1["state"] == 2
    assert review1["completed_at"] is not None

    # case4: update completed to in-progress
    req_update = {
        "review_id": review_id,
        "content": "update a content",
        "is_draft": True,
        "state": 1,
    }
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id, json=req_update, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 200

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert review1["content"] == "update a content"
    assert review1["is_draft"] is True
    assert review1["state"] == 1
    assert review1["completed_at"] is None


def test_review_delete_no_authorization(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = _create_initial_book(client, token)

    # create new review as precondition
    req_json = {
        "book_id": book_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    review_id = post_response1.json()["review_id"]
    # act: delete with no token
    put_response1 = client.delete(url=URL_BASE + "/" + review_id)
    assert put_response1.status_code == 401


def test_review_delete_not_existed_data(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)

    not_existed_review_id = "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"
    # act: delete
    put_response1 = client.delete(
        url=URL_BASE + "/" + not_existed_review_id, headers={"Authorization": "Bearer " + token}
    )
    assert put_response1.status_code == 404


def test_review_delete(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = _create_initial_book(client, token)

    # create new review as precondition
    req_json = {
        "book_id": book_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    post_response1 = client.post(url=URL_BASE, json=req_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    review_id = post_response1.json()["review_id"]

    # act: delete
    put_response1 = client.delete(url=URL_BASE + "/" + review_id, headers={"Authorization": "Bearer " + token})
    assert put_response1.status_code == 204

    # confirm with get response
    get_response1 = client.get(URL_BASE + "/me", headers={"Authorization": "Bearer " + token})
    assert get_response1.status_code == 200
    reviews = get_response1.json()["reviews"]
    assert len(reviews) == 0


def _create_initial_book(t_client: TestClient, token: str) -> str:
    url = "/api/books"
    request_json = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
    }
    post_response1 = t_client.post(url=url, json=request_json, headers={"Authorization": "Bearer " + token})
    assert post_response1.status_code == 200
    book_id = post_response1.json()["book_id"]
    assert book_id is not None
    return book_id


def _create_initial_books(t_client: TestClient, token: str) -> list[str]:
    url = "/api/books"
    request_json_list = [
        {
            "isbn13": "9784814400690",
            "title": "入門 継続的デリバリー",
            "publisher": "オライリージャパン",
            "authors": ["著者1", "著者2"],
            "published_at": "2023-01-10",
        },
        {
            "isbn13": "9784814400973",
            "title": "クリーンコードクックブック",
            "publisher": "オライリージャパン",
            "authors": ["著者A"],
            "published_at": "2024-01-10",
        },
        {
            "isbn13": "9784814400737",
            "title": "ドメイン駆動設計をはじめよう",
            "publisher": "オライリージャパン",
            "authors": ["著者X"],
            "published_at": "2023-06-10",
        },
    ]
    book_ids = []
    for request_json in request_json_list:
        post_response1 = t_client.post(url=url, json=request_json, headers={"Authorization": "Bearer " + token})
        assert post_response1.status_code == 200
        book_id = post_response1.json()["book_id"]
        assert book_id is not None
        book_ids.append(book_id)

    return book_ids
