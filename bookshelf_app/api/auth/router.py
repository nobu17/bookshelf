from enum import Enum

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4, BaseModel

from bookshelf_app.api.auth.service import (
    AuthService,
    LoginRequestAppModel,
    TokenUserAppModel,
)
from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.infra.dependencies import get_auth_service, get_user_dependency

router = CustomRouter()


class RoleEnum(str, Enum):
    admin = "admin"


class UserBaseModel(BaseModel):
    name: str
    email: str

    model_config = {"json_schema_extra": {"examples": [{"name": "nobu", "email": "hogehoge@hoge.com"}]}}


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class TokenUserModel(UserBaseModel):
    user_id: UUID4
    roles: list[str]


@router.post("/auth/token", response_model=TokenModel)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenModel:
    req = LoginRequestAppModel(form_data.username, form_data.password)
    token = auth_service.login(req)
    return TokenModel(**vars(token))


@router.get("/users/me", response_model=TokenUserModel)
async def get_current(current_user: TokenUserAppModel = Depends(get_user_dependency)) -> TokenUserModel:
    return TokenUserModel(**vars(current_user))
