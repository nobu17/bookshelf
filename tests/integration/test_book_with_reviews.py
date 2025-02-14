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
URL_REVIEW_BASE = "/api/reviews"

URL_WITH_REVIEW_BASE = "/api/book_with_reviews"
URL_WITH_REVIEW = URL_WITH_REVIEW_BASE + "/user_id"
URL_WITH_REVIEW_ME = URL_WITH_REVIEW_BASE + "/me"
URL_WITH_REVIEW_LATEST = URL_WITH_REVIEW_BASE + "/latest"


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

    get_json1 = response.json()
    assert len(get_json1["books_with_reviews"]) == 1
    book1 = get_json1["books_with_reviews"][0]
    book1_id = book1["book_id"]
    assert book1_id is not None
    assert book1["isbn13"] == "9784814400690"
    assert book1["title"] == "入門 継続的デリバリー"
    assert book1["publisher"] == "オライリージャパン"
    assert book1["published_at"] == "2023-01-10"
    assert book1["authors"][0] == "著者1"
    assert book1["authors"][1] == "著者2"

    # act2: get by user id
    user_id = get_user_id(client, token)
    response = client.get(URL_WITH_REVIEW + "/" + user_id, headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200

    get_json1 = response.json()
    assert len(get_json1["books_with_reviews"]) == 1
    book1 = get_json1["books_with_reviews"][0]
    book1_id = book1["book_id"]
    assert book1_id is not None
    assert book1["isbn13"] == "9784814400690"
    assert book1["title"] == "入門 継続的デリバリー"
    assert book1["publisher"] == "オライリージャパン"
    assert book1["published_at"] == "2023-01-10"
    assert book1["authors"][0] == "著者1"
    assert book1["authors"][1] == "著者2"

    # act3: get by latest
    response = client.get(URL_WITH_REVIEW_LATEST + "/100")
    assert response.status_code == 200

    get_json1 = response.json()
    assert len(get_json1["books_with_reviews"]) == 1
    book1 = get_json1["books_with_reviews"][0]
    book1_id = book1["book_id"]
    assert book1_id is not None
    assert book1["isbn13"] == "9784814400690"
    assert book1["title"] == "入門 継続的デリバリー"
    assert book1["publisher"] == "オライリージャパン"
    assert book1["published_at"] == "2023-01-10"
    assert book1["authors"][0] == "著者1"
    assert book1["authors"][1] == "著者2"


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
