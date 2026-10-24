from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shopping_db"

    # LLM Providers (Free Tier)
    gemini_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Server Settings
    port: int = 8000
    environment: str = "development"

    @property
    def active_gemini_api_key(self) -> str:
        return self.gemini_api_key or self.google_api_key


settings = Settings()

