from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_upload_size_bytes: int = 4_294_967_296
    # Used by JsonStore (fallback) when DATABASE_URL is not set.
    open_hoops_data_dir: Path = Path("/tmp/open-hoops")

    # Infrastructure — when DATABASE_URL is set, DatabaseStore is used.
    database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    ollama_host: str = "http://localhost:11434"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def psycopg2_url(self) -> str | None:
        """Strip asyncpg/aiosqlite driver qualifier so psycopg2 can accept the URL."""
        if self.database_url is None:
            return None
        return self.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")


settings = Settings()
