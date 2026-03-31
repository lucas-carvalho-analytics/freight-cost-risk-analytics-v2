from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "freight_cost_risk_analytics"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str | None = None
    jwt_secret_key: str = "change-this-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    log_level: str = "INFO"
    web_concurrency: int = 2

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

    def validate_runtime_security(self) -> None:
        if self.jwt_secret_key == "change-this-jwt-secret":
            raise RuntimeError(
                "JWT_SECRET_KEY is using the insecure default value. "
                "Set a real secret before starting the API."
            )

        if self.app_env.lower() == "production":
            if len(self.jwt_secret_key) < 32:
                raise RuntimeError(
                    "JWT_SECRET_KEY must have at least 32 characters in production."
                )
            if self.web_concurrency < 1:
                raise RuntimeError(
                    "WEB_CONCURRENCY must be greater than or equal to 1."
                )


settings = Settings()
