from fastapi import Depends

from bookshelf_app.api.auth.service import AuthService, TokenUserAppModel, oauth2_scheme
from bookshelf_app.api.tags.service import TagService
from bookshelf_app.infra.memory.auth import MemoryUserRepository
from bookshelf_app.infra.memory.tags import MemoryTagRepository
from bookshelf_app.infra.other.crypt import CryptService


def get_tag_memory_service() -> TagService:
    return TagService(MemoryTagRepository())


def get_auth_memory_service() -> AuthService:
    return AuthService(crypts=CryptService(), user_repos=MemoryUserRepository())


def get_admin_memory_dependency(token: str = Depends(oauth2_scheme)) -> TokenUserAppModel:
    return get_auth_memory_service().get_admin_user(token)


def get_user_memory_dependency(token: str = Depends(oauth2_scheme)) -> TokenUserAppModel:
    return get_auth_memory_service().get_current_user(token)
