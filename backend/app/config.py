from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://hackscore:hackscore@postgres:5432/hackscore"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me"
    upload_dir: str = "/app/uploads"
    api_prefix: str = "/api"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
