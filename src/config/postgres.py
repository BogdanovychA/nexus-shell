# -*- coding: utf-8 -*-

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
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.server}:{self.port}/{self.db}"


settings = PostgresConfig()
