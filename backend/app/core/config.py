from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Alex API"
    api_v1_prefix: str = "/api/v1"
    cors_origins_raw: str = "*"
    database_url: str | None = None
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.5-flash-lite"
    openrouter_site_url: str = "https://alex.local"
    openrouter_site_name: str = "Alex"
    clerk_jwks_url: str = "https://example.clerk.accounts.dev/.well-known/jwks.json"
    clerk_issuer: str = "https://example.clerk.accounts.dev"
    gcs_bucket_name: str = ""
    db_name: str = "alex"
    db_user: str = "alex"
    db_password: str = ""
    instance_connection_name: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @cached_property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.instance_connection_name and self.db_password:
            return (
                f"postgresql+pg8000://{self.db_user}:{self.db_password}@/{self.db_name}"
                f"?unix_sock=/cloudsql/{self.instance_connection_name}/.s.PGSQL.5432"
            )
        return "sqlite:///./alex.db"


settings = Settings()
