from bookshelf_app.api.auth.domain import Password, UserHashed, UserRoleEnum
from bookshelf_app.infra.db.auth import SqlUserRepository
from bookshelf_app.infra.db.database import get_session
from bookshelf_app.infra.other.crypt import CryptService
from bookshelf_app.tools.tool_config import get_tool_settings

settings = get_tool_settings()


def create_initial_admin() -> UserHashed:
    session_itr = get_session()
    repos = SqlUserRepository(session_itr.__next__())
    crypt = CryptService()
    password = Password(settings.tool_initial_user_pass)
    admin = UserHashed(
        name=settings.tool_initial_user_name,
        email=settings.tool_initial_user_mail,
        roles=[UserRoleEnum.Admin],
        hashed_password=crypt.create_hash(password),
    )
    return repos.create(admin)
