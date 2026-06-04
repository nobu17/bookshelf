# pylint: disable=unused-argument

import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.db.database import truncate_table, truncate_tables
from tests.integration.helper import (
    auth_headers,
    auth_as_admin,
    auth_as_user,
    create_initial_accounts,
    create_tag,
    delete_tag,
    get_tags,
    update_tag,
)

client = TestClient(main.app)

URL_BASE = "/api/tags"


@pytest.fixture(scope="class", autouse=True)
def scope_class():
    create_initial_accounts()
    yield
    truncate_tables()


@pytest.fixture(scope="function", autouse=True)
def scope_function():
    yield
    truncate_table("tags")


def test_tags_get_list_empty(database_service):
    # initial empty
    assert get_tags(client) == []


def test_tags_post_put_delete_successfully_as_admin():
    # precondition auth as admin user
    token = auth_as_admin(client)
    # case1: post new item
    resp_json = create_tag(client, token, "Test01")

    # get a post item to confirm
    assert get_tags(client) == [
        {"tag_id": resp_json["tag_id"], "name": "Test01"},
    ]

    # case2: put item
    update_tag(client, token, resp_json["tag_id"], "Test02")

    # get a put item to confirm
    assert get_tags(client) == [{"tag_id": resp_json["tag_id"], "name": "Test02"}]

    # delete item
    delete_tag(client, token, resp_json["tag_id"])

    # confirm empty
    assert get_tags(client) == []

    # case4: post new limit(15char)
    resp_json = create_tag(client, token, "123456789012345")

    # get a post item to confirm
    assert get_tags(client) == [{"tag_id": resp_json["tag_id"], "name": "123456789012345"}]


def test_tags_post_successfully_as_user():
    # precondition auth as normal user
    token = auth_as_user(client)
    # case1: post new item
    resp_json = create_tag(client, token, "123456789012345")

    # get a post item to confirm
    assert get_tags(client) == [
        {"tag_id": resp_json["tag_id"], "name": "123456789012345"},
    ]


def test_tags_put_delete_denied_as_user():
    # precondition auth as normal user
    token = auth_as_user(client)
    # post new item as preparation
    resp_json = create_tag(client, token, "Test01")

    # get a post item to confirm
    assert get_tags(client) == [
        {"tag_id": resp_json["tag_id"], "name": "Test01"},
    ]

    # case1: try put item and denied
    put_response = client.put(
        url=URL_BASE + f"/{resp_json['tag_id']}", json={"name": "Test02"}, headers=auth_headers(token)
    )
    assert put_response.status_code == 403

    # confirm put item is not modified
    assert get_tags(client) == [
        {"tag_id": resp_json["tag_id"], "name": "Test01"},
    ]

    # case2: try put item and denied
    get_response = client.delete(URL_BASE + f"/{resp_json['tag_id']}", headers=auth_headers(token))
    assert get_response.status_code == 403

    # confirm item is not deleted
    assert get_tags(client) == [
        {"tag_id": resp_json["tag_id"], "name": "Test01"},
    ]


def test_tags_post_unprocessable():
    # precondition auth as admin user
    token = auth_as_admin(client)
    # incorrect field
    post_response = client.post(url=URL_BASE, json={"nam": "Test01"}, headers=auth_headers(token))
    assert post_response.status_code == 422
    # empty name
    post_response = client.post(url=URL_BASE, json={"name": ""}, headers=auth_headers(token))
    assert post_response.status_code == 422
    # more than 16
    post_response = client.post(
        url=URL_BASE, json={"name": "1234567890123456"}, headers=auth_headers(token)
    )
    assert post_response.status_code == 422


def test_tags_post_conflict_duplicate_name():
    # precondition auth as admin user
    token = auth_as_admin(client)
    # post new item
    post_response1 = client.post(url=URL_BASE, json={"name": "Test0X"}, headers=auth_headers(token))
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()

    # post duplicated name item
    post_response2 = client.post(url=URL_BASE, json={"name": "Test0X"}, headers=auth_headers(token))
    assert post_response2.status_code == 409

    # confirm only 1 record
    get_response = client.get(URL_BASE)
    assert get_response.status_code == 200
    assert get_response.json() == [{"tag_id": post_json1["tag_id"], "name": "Test0X"}]


def test_tags_put_conflict_duplicate_name():
    # precondition auth as admin user
    token = auth_as_admin(client)
    # post 2 new items
    post_response1 = client.post(url=URL_BASE, json={"name": "Test01"}, headers=auth_headers(token))
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()

    post_response2 = client.post(url=URL_BASE, json={"name": "Test02"}, headers=auth_headers(token))
    assert post_response2.status_code == 200
    post_json2 = post_response2.json()

    # confirm 2 records
    get_response = client.get(URL_BASE)
    assert get_response.status_code == 200
    assert get_response.json() == [
        {"tag_id": post_json1["tag_id"], "name": "Test01"},
        {"tag_id": post_json2["tag_id"], "name": "Test02"},
    ]

    # put duplicate item
    put_response = client.put(
        url=URL_BASE + f"/{post_json2['tag_id']}",
        json={"name": "Test01"},
        headers=auth_headers(token),
    )
    assert put_response.status_code == 409

    # confirm 2 records are not changed
    get_response = client.get(URL_BASE)
    assert get_response.status_code == 200
    assert get_response.json() == [
        {"tag_id": post_json1["tag_id"], "name": "Test01"},
        {"tag_id": post_json2["tag_id"], "name": "Test02"},
    ]


def test_tags_put_not_exists_id():
    # precondition auth as admin user
    token = auth_as_admin(client)
    # post new item
    post_response1 = client.post(url=URL_BASE, json={"name": "Test0X"}, headers=auth_headers(token))
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()

    # try to delete another id
    get_response = client.put(
        URL_BASE + "/50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
        json={"name": "Test"},
        headers=auth_headers(token),
    )
    assert get_response.status_code == 404

    # confirm only 1 record
    get_response = client.get(URL_BASE)
    assert get_response.status_code == 200
    assert get_response.json() == [{"tag_id": post_json1["tag_id"], "name": "Test0X"}]


def test_tags_delete_not_exists_id():
    # precondition auth as admin user
    token = auth_as_admin(client)
    # post new item
    post_response1 = client.post(url=URL_BASE, json={"name": "Test0X"}, headers=auth_headers(token))
    assert post_response1.status_code == 200
    post_json1 = post_response1.json()

    # try to put another id
    get_response = client.delete(
        URL_BASE + "/50f65802-a5db-43cf-9dfc-3d5aea11d5dc", headers=auth_headers(token)
    )
    assert get_response.status_code == 404

    # confirm only 1 record
    get_response = client.get(URL_BASE)
    assert get_response.status_code == 200
    assert get_response.json() == [{"tag_id": post_json1["tag_id"], "name": "Test0X"}]
