# pylint: disable=E0213
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolSettings(BaseSettings):
    tool_initial_user_name: str = ""
    tool_initial_user_mail: str = ""
    tool_initial_user_pass: str = ""

    model_config = SettingsConfigDict(env_file=(".env.tool", ".env.tool.prod"), env_file_encoding="utf-8")

    @field_validator("tool_initial_user_name", mode="before")
    def validate_tool_initial_user_name_value(cls, v) -> str:
        if not v.strip():
            raise ValueError("tool_initial_user_name must not be empty")
        return v

    @field_validator("tool_initial_user_mail", mode="before")
    def validate_tool_initial_user_mail_value(cls, v) -> str:
        if not v.strip():
            raise ValueError("tool_initial_user_mail must not be empty")
        return v

    @field_validator("tool_initial_user_pass", mode="before")
    def validate_tool_initial_user_pass_value(cls, v) -> str:
        if not v.strip():
            raise ValueError("tool_initial_user_pass must not be empty")
        return v


@lru_cache()
def get_tool_settings() -> ToolSettings:
    return ToolSettings()
