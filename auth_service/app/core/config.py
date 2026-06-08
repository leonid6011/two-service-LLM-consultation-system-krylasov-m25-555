from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Auth Service"
    ENV: str = "development"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SQLITE_PATH: str = "auth.db"
    DATABASE_URL: str = "sqlite+aiosqlite:///auth.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
