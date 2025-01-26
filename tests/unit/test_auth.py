import pytest
from fastapi.testclient import TestClient

from bookshelf_app import main
from bookshelf_app.infra.dependencies import (
    get_admin_dependency,
    get_auth_service,
    get_user_dependency,
)
from bookshelf_app.infra.memory.dependencies import (
    get_admin_memory_dependency,
    get_auth_memory_service,
    get_user_memory_dependency,
)

client = TestClient(main.app)

URL_BASE = "/api/auth/token"
URL_ME = "/api/users/me"


@pytest.fixture(scope="class", autouse=True)
def scope_class():
    main.app.dependency_overrides[get_auth_service] = get_auth_memory_service
    main.app.dependency_overrides[get_admin_dependency] = get_admin_memory_dependency
    main.app.dependency_overrides[get_user_dependency] = get_user_memory_dependency
    yield
    main.app.dependency_overrides[get_auth_service] = get_auth_service
    main.app.dependency_overrides[get_admin_memory_dependency] = get_admin_dependency
    main.app.dependency_overrides[get_user_memory_dependency] = get_user_dependency


@pytest.fixture(scope="function", autouse=True)
def scope_function():
    yield


def test_auth_login_failed_invalid_input():
    # empty user name
    response = client.post(
        URL_BASE,
        data={"username": "", "password": "secret", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # not mail address
    response = client.post(
        URL_BASE,
        data={"username": "test", "password": "secret", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # username not existed
    response = client.post(
        URL_BASE,
        data={"_username": "test@test.com", "password": "", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # empty password
    response = client.post(
        URL_BASE,
        data={"username": "test@test.com", "password": "", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # password length 7
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "aB34567", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # password length 101
    response = client.post(
        URL_BASE,
        data={
            "username": "hoge@hoge.com",
            "password": "aB34567890" * 10 + "1",
            "grant_type": "password",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # password only num
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "12345678", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # password only num and lower
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "a12345678", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # password only num and upper
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "A12345678", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    # password only lower and upper
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "Aabcdefgh", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422


def test_auth_login_failed_auth():
    # email not exists
    response = client.post(
        URL_BASE,
        data={"username": "hoge2@hoge.com", "password": "Aa12345678", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401

    # password incorrect
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "Aa12345678", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_auth_login_success():
    response = client.post(
        URL_BASE,
        data={"username": "hoge@hoge.com", "password": "Hoge123456789", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    json = response.json()
    assert json["access_token"] != ""
    assert json["token_type"] == "bearer"

    # try get me
    me_response = client.get(
        URL_ME,
        headers={"Authorization": "Bearer " + json["access_token"]},
    )
    assert me_response.status_code == 200
    me_json = me_response.json()

    assert me_json["name"] == "admin"
    assert me_json["email"] == "hoge@hoge.com"
    assert me_json["roles"] == ["admin"]


def test_auth_access_failed_incorrect_token():
    # try get me with incorrect token
    me_response = client.get(
        URL_ME,
        headers={"Authorization": "Bearer AAAAAAAAAAAAAXXXXXXXX"},
    )
    assert me_response.status_code == 401
