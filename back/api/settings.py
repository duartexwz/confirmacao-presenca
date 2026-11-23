"""
Módulo de configuração da aplicação.
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Configurações da aplicação carregadas a partir de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DATABASE_URL_ENV: str = Field(default="", alias="DATABASE_URL")

    ACCESS_TOKEN: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @field_validator("DB_PORT", "ACCESS_TOKEN_EXPIRE_MINUTES", "ACCESS_TOKEN_EXPIRE_DAYS", mode="before")
    @classmethod
    def _empty_int(cls, value):
        if value == "" or value is None:
            return 30 if "ACCESS" not in "" else value
        return value

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES", mode="before")
    @classmethod
    def _empty_minutes(cls, value):
        if value == "" or value is None:
            return 30
        return value

    @field_validator("ACCESS_TOKEN_EXPIRE_DAYS", mode="before")
    @classmethod
    def _empty_days(cls, value):
        if value == "" or value is None:
            return 7
        return value

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def _empty_port(cls, value):
        if value == "" or value is None:
            return 5432
        return value

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def _empty_secret(cls, value):
        if value == "" or value is None:
            return "dev-secret-key-change-me"
        return value

    @field_validator("ALGORITHM", mode="before")
    @classmethod
    def _empty_algo(cls, value):
        if value == "" or value is None:
            return "HS256"
        return value

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        if self.DATABASE_URL_ENV:
            return self.DATABASE_URL_ENV
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
