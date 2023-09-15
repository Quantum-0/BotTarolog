from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_")

    LEVEL: str = "INFO"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    ENGINE: Literal["postgresql", "sqlite"]
    HOST: str = ""
    PORT: int = 5432
    USER: str = ""
    PASS: str = ""
    DB: str = "postgres"
    METRICS_TABLE_NAME: str = "tarolog_bot_metrics"

    @property
    def DSN(self) -> str:
        return f"postgresql://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.DB}"


class SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    DSN: str | None = None
    TRACES_SAMPLE_RATE: float = 1


class Settings(BaseSettings):
    Sentry: SentrySettings = Field(default_factory=SentrySettings)
    Database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    Logging: LoggingSettings = Field(default_factory=LoggingSettings)

    BOT_TOKEN: str
    API_BASE_URL: str
    SALT: str = "SOME_DEFAULT_SALT_VALUE"


settings = Settings()
