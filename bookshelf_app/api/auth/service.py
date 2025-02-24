import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from fastapi.security import OAuth2PasswordBearer

from bookshelf_app.api.auth.domain import (
    Email,
    ICryptService,
    IUserRepository,
    LoginRequest,
)
from bookshelf_app.api.shared.errors import (
    AuthCredentialsError,
    AuthFailedError,
    AuthRolePermissionError,
)


@dataclass(frozen=True)
class LoginRequestAppModel:
    email: str
    password: str


class UserAppRoleEnum(StrEnum):
    Admin = "admin"

    @classmethod
    def value_of(cls: type[Self], target_value: str) -> Self:
        for e in UserAppRoleEnum:
            if e.value == target_value:
                return cls(e)

        raise ValueError(f"{target_value} not matched type.")


@dataclass(frozen=True)
class TokenUserAppModel:
    user_id: uuid.UUID
    name: str
    email: str
    roles: list[UserAppRoleEnum]

    def is_admin(self) -> bool:
        return UserAppRoleEnum.Admin in self.roles


@dataclass(frozen=True)
class TokenAppModel:
    access_token: str
    token_type: str
    user: TokenUserAppModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


class AuthService:
    _user_repos: IUserRepository
    _crypts: ICryptService

    def __init__(self, user_repos: IUserRepository, crypts: ICryptService):
        self._user_repos = user_repos
        self._crypts = crypts

    def login(self, req: LoginRequestAppModel) -> TokenAppModel:
        domain_req = LoginRequest(req.email, req.password)

        user = self._user_repos.find_by_email(domain_req.email)
        if not user:
            raise AuthFailedError(f"user not exists. email:{req.email}")

        if not self._crypts.verify(domain_req.password, user.hashed_password):
            raise AuthFailedError(f"password invalid. password:{domain_req.password}")

        token = self._crypts.create_token(user)
        user_app = TokenUserAppModel(
            user_id=user.user_id,
            name=user.name.value,
            email=user.email.value,
            roles=[UserAppRoleEnum.value_of(str(role)) for role in user.roles],
        )
        return TokenAppModel(
            token_type=token.token_type,
            access_token=token.access_token,
            user=user_app,
        )

    def get_current_user(self, token: str) -> TokenUserAppModel:
        decoded_token = self._crypts.decode_token(token)
        email = Email(decoded_token.email)
        user = self._user_repos.find_by_email(email)
        if user is None:
            raise AuthCredentialsError(detail=f"user not exists from db. id={decoded_token.email}")

        return TokenUserAppModel(
            user_id=user.user_id,
            name=user.name.value,
            email=user.email.value,
            roles=[UserAppRoleEnum.value_of(str(role)) for role in user.roles],
        )

    def get_admin_user(self, token: str) -> TokenUserAppModel:
        user = self.get_current_user(token)
        if not user.is_admin():
            raise AuthRolePermissionError(str(UserAppRoleEnum.Admin))

        return user


# class AuthUserDependency:
#     _auth_service: AuthService

#     def __init__(self, auth_service: AuthService):
#         self._auth_service = auth_service

#     async def __call__(self, token: str = Depends(oauth2_scheme)) -> TokenUserAppModel:
#         return self._auth_service.get_current_user(token)


# class AuthAdminDependency(AuthUserDependency):

#     async def __call__(self, token: str = Depends(oauth2_scheme)) -> TokenUserAppModel:
#         user = self._auth_service.get_current_user(token)
#         if UserAppRoleEnum.Admin not in user.roles:
#             raise AuthRolePermissionError(str(UserAppRoleEnum.Admin))

#         return user
