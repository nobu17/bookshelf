# pylint: disable=E0213
from functools import lru_cache
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# https://scrapbox.io/mayoumelon-log/FastAPIで.envに定義した変数を利用する


class Settings(BaseSettings):
    crypt_secret_key: str = ""
    crypt_algorithm: str = ""
    db_connection: str = ""

    model_config = SettingsConfigDict(env_file=(os.getenv("ENV_FILE", ".env"), ".env.prod"), env_file_encoding="utf-8")

    @field_validator("crypt_secret_key", mode="before")
    def validate_crypt_secret_key_value(cls, v) -> str:
        if not v.strip():
            raise ValueError("crypt_secret_key must not be empty")
        return v

    @field_validator("crypt_algorithm", mode="before")
    def validate_crypt_algorithm_value(cls, v) -> str:
        acceptable = ["HS256", "RS256"]
        if v not in acceptable:
            raise ValueError(f"crypt_algorithm should be match acceptable list. list:{acceptable}, current:{v}")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()
