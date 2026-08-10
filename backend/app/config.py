import os
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuracoes da aplicacao - suporta SQLite local e PostgreSQL online."""

    # URL completa do banco, usada por plataformas como Render/Railway.
    database_url: Optional[str] = None

    # Escolher qual banco usar: "sqlite" (padrao) ou "postgresql".
    db_type: str = os.getenv("DB_TYPE", "sqlite")

    # Database credentials (PostgreSQL).
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "bartcellos_loyalty")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")

    # SQLite path.
    sqlite_path: str = os.getenv("SQLITE_PATH", "./bartcellos_loyalty.db")

    # JWT.
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App.
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../.env")
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value):
        """Aceita valores de ambiente usados por plataformas de deploy."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod", "false", "0", "no", "off"}:
                return False
            if normalized in {"debug", "development", "dev", "true", "1", "yes", "on"}:
                return True
        return value

    def get_database_url(self) -> str:
        """Retorna URL do banco selecionado."""
        if self.database_url:
            if self.database_url.startswith("postgresql://"):
                return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
            if self.database_url.startswith("postgres://"):
                return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
            return self.database_url

        if self.db_type.lower() == "postgresql":
            return (
                f"postgresql+psycopg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )

        return f"sqlite:///{self.sqlite_path}"

    def get_database_info(self) -> str:
        """Retorna informacoes sobre qual banco esta sendo usado."""
        if self.database_url:
            return "PostgreSQL (DATABASE_URL)"
        if self.db_type.lower() == "postgresql":
            return f"PostgreSQL ({self.db_host}:{self.db_port}/{self.db_name})"
        return f"SQLite ({os.path.abspath(self.sqlite_path)})"


settings = Settings()
