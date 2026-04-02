# -*- coding: utf-8 -*-

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import bot


class PostgresConfig(BaseSettings):
    server: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    db: str | None = None

    model_config = SettingsConfigDict(
        env_file=bot.settings.base_dir / ".env",
        env_prefix="POSTGRES_",
        extra="ignore",
    )

    @property
    def url(self) -> str:

        user = quote_plus(str(self.user))
        password = quote_plus(str(self.password))

        return f"postgresql+asyncpg://{user}:{password}@{self.server}:{self.port}/{self.db}"


settings = PostgresConfig()
