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

    @staticmethod
    def _is_placeholder_secret(value: str) -> bool:
        placeholders = {
            "change-this-jwt-secret",
            "replace-with-a-long-random-secret-for-demo",
            "replace-with-a-long-random-secret-with-at-least-32-characters",
        }
        return value in placeholders

    @staticmethod
    def _is_unsafe_postgres_password(value: str) -> bool:
        unsafe_passwords = {
            "postgres",
            "replace-with-a-strong-password",
        }
        return value in unsafe_passwords

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

        app_env = self.app_env.lower()

        if app_env in {"demo", "production"} and self._is_placeholder_secret(
            self.jwt_secret_key
        ):
            raise RuntimeError(
                "JWT_SECRET_KEY is still using a placeholder value for demo/production."
            )

        if app_env in {"demo", "production"} and len(self.jwt_secret_key) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY must have at least 32 characters in demo/production."
            )

        if self.access_token_expire_minutes < 5:
            raise RuntimeError(
                "ACCESS_TOKEN_EXPIRE_MINUTES must be greater than or equal to 5."
            )

        if app_env == "production":
            if self.web_concurrency < 1:
                raise RuntimeError(
                    "WEB_CONCURRENCY must be greater than or equal to 1."
                )
            if self._is_unsafe_postgres_password(self.postgres_password):
                raise RuntimeError(
                    "POSTGRES_PASSWORD is using an unsafe placeholder/default value "
                    "for production."
                )


settings = Settings()
