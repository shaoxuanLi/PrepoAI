from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PrepoAI Backend"
    api_v1_prefix: str = "/api/v1"

    postgres_dsn: str = "postgresql+asyncpg://prepoai:prepoai@postgres:5432/prepoai"
    mongo_dsn: str = "mongodb://mongodb:27017"
    mongo_db_name: str = "prepoai"
    redis_dsn: str = "redis://redis:6379/0"

    secret_key: str = "replace-this-in-production"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
