# -*- coding: utf-8 -*-

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import bot


class MongoConfig(BaseSettings):
    server: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    db: str = "nexus-shell"
    main_collection: str = "users"
    uri: str | None = None

    model_config = SettingsConfigDict(
        env_file=bot.settings.base_dir / ".env",
        env_prefix="MONGO_INITDB_ROOT_",
        extra="ignore",
    )

    @property
    def url(self) -> str:

        if self.uri:
            return self.uri
        else:
            user = quote_plus(str(self.username))
            password = quote_plus(str(self.password))

            return f"mongodb://{user}:{password}@{self.server}:{self.port}/"


settings = MongoConfig()
