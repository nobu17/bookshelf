# pylint: disable=unused-argument

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.db.database import truncate_table, truncate_tables
from tests.integration.helper import (
    assert_review_response,
    auth_as_admin,
    auth_as_user,
    auth_headers,
    create_book,
    create_book_ids,
    create_initial_accounts,
    create_review,
    default_review_update_request,
    delete_review,
    default_review_request,
    get_latest_reviews,
    get_my_reviews,
    update_review,
)

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

    assert get_my_reviews(client, token) == []


def test_review_post_create_not_authorized(database_service):
    # prepare token for creating book data as initial
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    # send without authorization token
    post_response1 = client.post(url=URL_BASE, json=default_review_request(book_id))
    assert post_response1.status_code == 401


def test_review_post_create(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_ids = create_book_ids(client, token)

    # case1: create with not yet
    req_json = default_review_request(book_ids[0], content="")
    create_review(client, token, book_ids[0], content="")

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    assert_review_response(reviews[0], req_json)
    assert reviews[0]["last_modified_at"] is not None

    # case2: create with in progress
    req_json = default_review_request(book_ids[1], content="In prog", state=1)
    create_review(client, token, book_ids[1], content="In prog", state=1)

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 2
    assert_review_response(reviews[1], req_json)
    assert reviews[1]["last_modified_at"] is not None

    # case3: create with completed
    req_json = default_review_request(book_ids[2], content="Good book.", state=2, completed_at="2024-12-12 10:05")
    create_review(client, token, book_ids[2], content="Good book.", state=2, completed_at="2024-12-12 10:05")

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 3
    assert_review_response(reviews[2], req_json)
    assert reviews[2]["last_modified_at"] is not None

    # confirm with latest
    reviews = get_latest_reviews(client, token, 100)
    assert len(reviews) == 3

    # confirm with 2 latest
    reviews = get_latest_reviews(client, token, 2)
    assert len(reviews) == 2


def test_review_post_create_same_book_review(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # case1: create new completed review
    req_json = default_review_request(book_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30")
    create_review(client, token, book_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30")

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    assert_review_response(reviews[0], req_json)

    # case2: create additional review of same book and other state (not yet)
    req_json = default_review_request(book_id, content="this is my second review.", is_draft=True)
    create_review(client, token, book_id, content="this is my second review.", is_draft=True)

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 2
    assert_review_response(reviews[1], req_json)

    # case3: create new completed review again
    req_json = default_review_request(
        book_id,
        content="this is my third review.",
        state=2,
        completed_at="2034-04-23T10:20:30.400+02:30",
    )
    create_review(
        client,
        token,
        book_id,
        content="this is my third review.",
        state=2,
        completed_at="2034-04-23T10:20:30.400+02:30",
    )

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 3
    assert_review_response(reviews[2], req_json)


def test_review_post_create_same_book_review_invalid_state_not_yet(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # preparation1: create new completed review
    create_review(client, token, book_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30")

    # preparation2: create new not-yet review
    create_review(client, token, book_id, content="this is my second review.")

    # case1: create not yet review
    req_json = default_review_request(book_id, content="this is my third review.")
    post_response1 = client.post(url=URL_BASE, json=req_json, headers=auth_headers(token))
    assert post_response1.status_code == 422

    # case2: create in-progress review
    req_json = default_review_request(book_id, content="this is my third review.", state=1)
    post_response1 = client.post(url=URL_BASE, json=req_json, headers=auth_headers(token))
    assert post_response1.status_code == 422


def test_review_post_create_same_book_review_invalid_state_in_progress(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # preparation1: create new completed review
    create_review(client, token, book_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30")

    # preparation2: create new in-progress review
    create_review(client, token, book_id, content="this is my second review.", state=1)

    # case1: create not yet review
    req_json = default_review_request(book_id, content="this is my third review.")
    post_response1 = client.post(url=URL_BASE, json=req_json, headers=auth_headers(token))
    assert post_response1.status_code == 422

    # case2: create in-progress review
    req_json = default_review_request(book_id, content="this is my third review.", state=1)
    post_response1 = client.post(url=URL_BASE, json=req_json, headers=auth_headers(token))
    assert post_response1.status_code == 422


def test_review_post_create_completed_requires_completed_at(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    response = client.post(
        url=URL_BASE,
        json=default_review_request(book_id, state=2, completed_at=None),
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_review_post_create_rejects_invalid_state(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    response = client.post(url=URL_BASE, json=default_review_request(book_id, state=3), headers=auth_headers(token))

    assert response.status_code == 422


@pytest.mark.parametrize(
    ["content", "expected_status"],
    [
        pytest.param("x" * 10000, 200, id="10000 length"),
        pytest.param("x" * 10001, 422, id="10001 length"),
    ],
)
def test_review_post_create_content_length_boundary(database_service, content: str, expected_status: int):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]

    response = client.post(
        url=URL_BASE,
        json=default_review_request(book_id, content=content),
        headers=auth_headers(token),
    )

    assert response.status_code == expected_status


def test_review_post_create_preserves_completed_state_datetime_instant(database_service):
    token = auth_as_user(client)
    book_id = create_book(client, token)["book_id"]
    completed_at = "2032-04-23T10:20:30.400+02:30"

    create_review(client, token, book_id, state=2, completed_at=completed_at)

    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    assert reviews[0]["state"] == 2
    assert _parse_iso_datetime(reviews[0]["completed_at"]) == _parse_iso_datetime(completed_at)


def test_review_put_update_not_existed_data(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)

    not_existed_review_id = "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"
    req_update = default_review_update_request(content="not existed")
    put_response1 = client.put(
        url=URL_BASE + "/" + not_existed_review_id, json=req_update, headers=auth_headers(token)
    )
    assert put_response1.status_code == 422


def test_review_put_no_authorization(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # create new review as precondition
    review_id = create_review(client, token, book_id)["review_id"]

    # try to update without token
    req_update = default_review_update_request()
    put_response1 = client.put(url=URL_BASE + "/" + review_id, json=req_update)
    assert put_response1.status_code == 401


def test_review_put_update(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # create new review as precondition
    review_id = create_review(client, token, book_id)["review_id"]

    # case1: update content and draft
    req_update = default_review_update_request()
    update_review(client, token, review_id)

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert_review_response(review1, {"book_id": book_id, **req_update})

    # case2: update state not yet to in-progress
    req_update = default_review_update_request(state=1)
    update_review(client, token, review_id, state=1)

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert_review_response(review1, {"book_id": book_id, **req_update})

    # case3: update in-progress to completed
    req_update = default_review_update_request(state=2, completed_at="2032-04-23T10:20:30.400+02:30")
    update_review(client, token, review_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30")

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert_review_response(review1, {"book_id": book_id, **req_update})

    # case4: update completed to in-progress
    req_update = default_review_update_request(state=1)
    update_review(client, token, review_id, state=1)

    # confirm with get response
    reviews = get_my_reviews(client, token)
    assert len(reviews) == 1
    review1 = reviews[0]
    assert review1["review_id"] == review_id
    assert review1["book_id"] == book_id
    assert_review_response(review1, {"book_id": book_id, **req_update})


def test_review_put_update_invalid_state_not_yet(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # precondition1: create new review as completed
    review_id1 = create_review(
        client, token, book_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30"
    )["review_id"]

    # precondition2: create new review as not-yet
    create_review(client, token, book_id)

    # case1: update completed -> not-yet
    req_update = default_review_update_request(is_draft=False)
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id1, json=req_update, headers=auth_headers(token)
    )
    assert put_response1.status_code == 422

    # case2: update completed -> in-progress
    req_update = default_review_update_request(is_draft=False, state=1)
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id1, json=req_update, headers=auth_headers(token)
    )
    assert put_response1.status_code == 422


def test_review_put_update_invalid_state_in_progress(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # precondition1: create new review as completed
    review_id1 = create_review(
        client, token, book_id, state=2, completed_at="2032-04-23T10:20:30.400+02:30"
    )["review_id"]

    # precondition2: create new review as in-progress
    create_review(client, token, book_id, state=1)

    # case1: update completed -> not-yet
    req_update = default_review_update_request(is_draft=False)
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id1, json=req_update, headers=auth_headers(token)
    )
    assert put_response1.status_code == 422

    # case2: update completed -> in-progress
    req_update = default_review_update_request(is_draft=False, state=1)
    put_response1 = client.put(
        url=URL_BASE + "/" + review_id1, json=req_update, headers=auth_headers(token)
    )
    assert put_response1.status_code == 422


def test_review_put_update_denies_another_user_data(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    book_id = create_book(client, admin_token)["book_id"]
    review_id = create_review(client, admin_token, book_id)["review_id"]

    response = client.put(
        url=URL_BASE + "/" + review_id,
        json=default_review_update_request(content="try to update another user review"),
        headers=auth_headers(user_token),
    )

    assert response.status_code == 401


def test_review_delete_no_authorization(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # create new review as precondition
    review_id = create_review(client, token, book_id)["review_id"]
    # act: delete with no token
    put_response1 = client.delete(url=URL_BASE + "/" + review_id)
    assert put_response1.status_code == 401


def test_review_delete_not_existed_data(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)

    not_existed_review_id = "50f65802-a5db-43cf-9dfc-3d5aea11d5dc"
    # act: delete
    put_response1 = client.delete(
        url=URL_BASE + "/" + not_existed_review_id, headers=auth_headers(token)
    )
    assert put_response1.status_code == 404


def test_review_delete(database_service):
    # precondition auth as normal user
    token = auth_as_user(client)
    # create book at first
    book_id = create_book(client, token)["book_id"]

    # create new review as precondition
    review_id = create_review(client, token, book_id)["review_id"]

    # act: delete
    delete_review(client, token, review_id)

    # confirm with get response
    assert get_my_reviews(client, token) == []

    get_deleted_response = client.get(URL_BASE + "/find?review_id=" + review_id)
    assert get_deleted_response.status_code == 404


def test_review_delete_denies_another_user_data(database_service):
    user_token = auth_as_user(client)
    admin_token = auth_as_admin(client)
    book_id = create_book(client, admin_token)["book_id"]
    review_id = create_review(client, admin_token, book_id)["review_id"]

    response = client.delete(url=URL_BASE + "/" + review_id, headers=auth_headers(user_token))

    assert response.status_code == 401


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
