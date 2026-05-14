from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = Field(default="Document Processing API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    uploads_dir: str = Field(default="uploads", alias="UPLOADS_DIR")

    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_user: str = Field(default="root", alias="DB_USER")
    db_password: str = Field(default="root", alias="DB_PASSWORD")
    db_name: str = Field(default="document_db", alias="DB_NAME")

    @property
    def database_url(self) -> str:
        # MySQL async driver
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Allow local `.env` support in development; container/platform env vars still win.
    load_dotenv(override=False)
    return Settings()
