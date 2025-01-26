from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from bookshelf_app.api.auth.domain import (
    DecodeTokenData,
    HashedPassword,
    ICryptService,
    Password,
    Token,
    UserBase,
)
from bookshelf_app.api.shared.errors import AuthCredentialsError
from bookshelf_app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class CryptService(ICryptService):
    access_token_expire_minutes = 30
    secret_key = ""
    algorithm = ""

    def __init__(self):
        self.secret_key = get_settings().crypt_secret_key
        self.algorithm = get_settings().crypt_algorithm

    def create_hash(self, password: Password) -> str:
        hash = pwd_context.hash(password.value)
        return hash

    def verify(self, plain_pass: Password, hashed_pass: HashedPassword) -> bool:
        return pwd_context.verify(plain_pass.value, hashed_pass.value)

    def create_token(self, user: UserBase) -> Token:
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        data = dict()
        data["sub"] = user.email.value
        access_token = self._create_access_token(data=data, expires_delta=access_token_expires)
        return Token(access_token=access_token)

    def decode_token(self, token: str) -> DecodeTokenData:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            sub_val = payload.get("sub")
            if sub_val is None or not isinstance(sub_val, str):
                raise AuthCredentialsError(detail="no user.")

            return DecodeTokenData(email=sub_val)
        except JWTError as exc:
            raise AuthCredentialsError(detail=f"JWTError:{exc}") from exc

    def _create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
