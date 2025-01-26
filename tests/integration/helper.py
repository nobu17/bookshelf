from fastapi.testclient import TestClient

from bookshelf_app.api.auth.domain import Password, UserHashed, UserRoleEnum
from bookshelf_app.infra.db.auth import SqlUserRepository
from bookshelf_app.infra.db.database import get_session
from bookshelf_app.infra.other.crypt import CryptService

AUTH_URL = "/api/auth/token"
ME_URL = "/api/users/me"


def create_initial_admin():
    session_itr = get_session()
    repos = SqlUserRepository(session_itr.__next__())
    crypt = CryptService()
    password = Password("Hoge123456789")
    admin = UserHashed(
        name="admin",
        email="hoge@hoge.com",
        roles=[UserRoleEnum.Admin],
        hashed_password=crypt.create_hash(password),
    )
    repos.create(admin)


def create_initial_user():
    repos = SqlUserRepository(get_session)
    crypt = CryptService()
    password = Password("ABCabc12345")
    user = UserHashed(name="user", email="user@user.com", roles=[], hashed_password=crypt.create_hash(password))
    repos.create(user)


def create_initial_accounts():
    for session in get_session():
        repos = SqlUserRepository(session)
        crypt = CryptService()
        password1 = Password("Hoge123456789")
        admin = UserHashed(
            name="admin",
            email="hoge@hoge.com",
            roles=[UserRoleEnum.Admin],
            hashed_password=crypt.create_hash(password1),
        )
        repos.create(admin)

        password2 = Password("ABCabc12345")
        user = UserHashed(name="user", email="user@user.com", roles=[], hashed_password=crypt.create_hash(password2))
        repos.create(user)

        session.close()


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


def get_user_id(client: TestClient, token: str) -> str:
    # email not exists
    response = client.get(ME_URL, headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    json = response.json()
    assert json["user_id"] is not None

    return json["user_id"]
