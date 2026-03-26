from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "freight_cost_risk_analytics"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "freight_analytics"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
