from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allowed_origins: str = "http://localhost:3000"
    max_upload_size_bytes: int = 4_294_967_296
    # Docker Compose overrides this with a named volume for persistence.
    open_hoops_data_dir: Path = Path("/tmp/open-hoops")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
