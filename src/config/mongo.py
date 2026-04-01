# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import bot


class MongoConfig(BaseSettings):
    server: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    db: str = "nexus-shell"
    main_collection: str = "users"

    model_config = SettingsConfigDict(
        env_file=bot.settings.base_dir / ".env",
        env_prefix="MONGO_INITDB_ROOT_",
        extra="ignore",
    )

    @property
    def url(self) -> str:
        return f"mongodb://{self.username}:{self.password}@{self.server}:{self.port}/"


settings = MongoConfig()
