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


class TokenData(BaseModel):
    username: str | None = None


class TokenUserModel(UserBaseModel):
    user_id: UUID4
    roles: list[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "nobu",
                    "email": "hogehoge@hoge.com",
                    "user_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                    "roles": ["admin"],
                }
            ]
        }
    }


class TokenModel(BaseModel):
    access_token: str
    token_type: str
    user: TokenUserModel

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "xxxxx",
                    "token_type": "bearer",
                    "user": {
                        "name": "nobu",
                        "email": "hogehoge@hoge.com",
                        "user_id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                        "roles": ["admin"],
                    },
                }
            ]
        }
    }


@router.post("/auth/token", response_model=TokenModel)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenModel:
    req = LoginRequestAppModel(form_data.username, form_data.password)
    token = auth_service.login(req)
    usr = TokenUserModel(
        name=token.user.name,
        email=token.user.email,
        user_id=token.user.user_id,
        roles=[x for x in token.user.roles],
    )
    return TokenModel(
        access_token=token.access_token,
        token_type=token.token_type,
        user=usr,
    )


@router.get("/users/me", response_model=TokenUserModel)
async def get_current(current_user: TokenUserAppModel = Depends(get_user_dependency)) -> TokenUserModel:
    return TokenUserModel(**vars(current_user))
