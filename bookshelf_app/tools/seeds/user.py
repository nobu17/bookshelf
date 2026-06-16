from dataclasses import dataclass

from bookshelf_app.api.auth.domain import Email, Password, UserHashed, UserRoleEnum
from bookshelf_app.infra.db.auth import SqlUserRepository
from bookshelf_app.infra.db.database import get_session
from bookshelf_app.infra.other.crypt import CryptService
from bookshelf_app.tools.tool_config import get_tool_settings


@dataclass(frozen=True)
class InitialAdminResult:
    user: UserHashed
    created: bool


def create_initial_admin() -> UserHashed:
    return ensure_initial_admin().user


def ensure_initial_admin() -> InitialAdminResult:
    settings = get_tool_settings()
    password = Password(settings.tool_initial_user_pass)
    email = Email(settings.tool_initial_user_mail)

    for session in get_session():
        repos = SqlUserRepository(session)
        existing = repos.find_by_email(email)
        if existing is not None:
            return InitialAdminResult(user=existing, created=False)

        crypt = CryptService()
        admin = UserHashed(
            name=settings.tool_initial_user_name,
            email=email.value,
            roles=[UserRoleEnum.Admin],
            hashed_password=crypt.create_hash(password),
        )
        return InitialAdminResult(user=repos.create(admin), created=True)

    raise RuntimeError("failed to open database session")


def main() -> None:
    result = ensure_initial_admin()
    status = "created" if result.created else "already exists"
    print(f"initial admin {status}: {result.user.email.value}")


if __name__ == "__main__":
    main()
