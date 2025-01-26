from fastapi.testclient import TestClient

AUTH_URL = "/api/auth/token"


def auth_as_admin(client: TestClient) -> str:
    # email not exists
    response = client.post(
        AUTH_URL,
        data={"username": "hoge@hoge.com", "password": "Hoge123456789", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    json = response.json()
    assert json["access_token"] != ""
    assert json["token_type"] == "bearer"

    return json["access_token"]


def auth_as_user(client: TestClient) -> str:
    # email not exists
    response = client.post(
        AUTH_URL,
        data={"username": "user@user.com", "password": "ABCabc12345", "grant_type": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    json = response.json()
    assert json["access_token"] != ""
    assert json["token_type"] == "bearer"

    return json["access_token"]
