from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Bot Service"
    ENV: str = "development"

    BOT_TOKEN: str = "your-telegram-bot-token"

    AUTH_SERVICE_URL: str = "http://localhost:8000"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALG: str = "HS256"

    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    REDIS_URL: str = "redis://redis:6379/0"

    OPENROUTER_API_KEY: str = "your-openrouter-api-key"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "stepfun/step-3.5-flash:free"
    OPENROUTER_SITE_URL: str = "https://example.com"
    OPENROUTER_APP_NAME: str = "bot-service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
