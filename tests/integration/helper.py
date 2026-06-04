from fastapi.testclient import TestClient

from bookshelf_app.api.auth.domain import Password, UserHashed, UserRoleEnum
from bookshelf_app.infra.db.auth import SqlUserRepository
from bookshelf_app.infra.db.database import get_session
from bookshelf_app.infra.other.crypt import CryptService

AUTH_URL = "/api/auth/token"
ME_URL = "/api/users/me"
BOOKS_URL = "/api/books"
TAGS_URL = "/api/tags"
REVIEWS_URL = "/api/reviews"


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
    response = client.get(ME_URL, headers=auth_headers(token))
    assert response.status_code == 200
    json = response.json()
    assert json["user_id"] is not None

    return json["user_id"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + token}


def default_book_request(**overrides) -> dict:
    request = {
        "isbn13": "9784814400690",
        "title": "入門 継続的デリバリー",
        "publisher": "オライリージャパン",
        "authors": ["著者1", "著者2"],
        "published_at": "2023-01-10",
        "image_url": "",
    }
    request.update(overrides)
    return request


def create_book(client: TestClient, token: str, **overrides) -> dict:
    response = client.post(url=BOOKS_URL, json=default_book_request(**overrides), headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()
    assert body["book_id"] is not None
    return body


def create_book_ids(client: TestClient, token: str) -> list[str]:
    books = [
        create_book(client, token),
        create_book(
            client,
            token,
            isbn13="9784814400973",
            title="クリーンコードクックブック",
            authors=["著者A"],
            published_at="2024-01-10",
        ),
        create_book(
            client,
            token,
            isbn13="9784814400737",
            title="ドメイン駆動設計をはじめよう",
            authors=["著者X"],
            published_at="2023-06-10",
        ),
    ]
    return [book["book_id"] for book in books]


def create_tags(client: TestClient, token: str, names: list[str] | None = None) -> list[str]:
    tag_ids: list[str] = []
    for name in names or ["Tag1", "Tag2", "Tag3"]:
        tag_ids.append(create_tag(client, token, name)["tag_id"])
    return tag_ids


def create_tag(client: TestClient, token: str, name: str) -> dict:
    response = client.post(url=TAGS_URL, json={"name": name}, headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()


def get_tags(client: TestClient) -> list[dict]:
    response = client.get(TAGS_URL)
    assert response.status_code == 200
    return response.json()


def update_tag(client: TestClient, token: str, tag_id: str, name: str) -> None:
    response = client.put(url=TAGS_URL + f"/{tag_id}", json={"name": name}, headers=auth_headers(token))
    assert response.status_code == 200


def delete_tag(client: TestClient, token: str, tag_id: str) -> None:
    response = client.delete(TAGS_URL + f"/{tag_id}", headers=auth_headers(token))
    assert response.status_code == 204


def assert_book_response(book: dict, expected: dict) -> None:
    assert book["book_id"] is not None
    assert book["isbn13"] == expected["isbn13"]
    assert book["title"] == expected["title"]
    assert book["publisher"] == expected["publisher"]
    assert book["published_at"] == expected["published_at"]
    assert book["image_url"] == expected.get("image_url", "")
    assert sorted(book["authors"]) == sorted(expected["authors"])


def default_review_request(book_id: str, **overrides) -> dict:
    request = {
        "book_id": book_id,
        "content": "this is my first review.",
        "is_draft": False,
        "state": 0,
    }
    request.update(overrides)
    return request


def create_review(client: TestClient, token: str, book_id: str, **overrides) -> dict:
    response = client.post(
        url=REVIEWS_URL,
        json=default_review_request(book_id, **overrides),
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["review_id"] is not None
    return body


def get_my_reviews(client: TestClient, token: str) -> list[dict]:
    response = client.get(REVIEWS_URL + "/me", headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()["reviews"]


def get_latest_reviews(client: TestClient, token: str, max_count: int) -> list[dict]:
    response = client.get(REVIEWS_URL + f"/latest/{max_count}", headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()["reviews"]


def assert_review_response(review: dict, expected: dict) -> None:
    assert review["review_id"] is not None
    assert review["book_id"] == expected["book_id"]
    assert review["content"] == expected["content"]
    assert review["is_draft"] is expected["is_draft"]
    assert review["state"] == expected["state"]
    if expected.get("completed_at") is None:
        assert review["completed_at"] is None
    else:
        assert review["completed_at"] is not None
