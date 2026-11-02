"""Configuración de la aplicación, leída del entorno (.env).

Ningún secreto vive en el código: todo llega por variables de entorno.
"""
import logging
import secrets
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("gis.config")

MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./gis.db"
    cors_origins: str = "http://localhost:5173"
    cookie_name: str = "access_token"

    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = ""

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]

    @model_validator(mode="after")
    def _validar_secret_key(self) -> "Settings":
        if self.is_production:
            # Mejor que la app no arranque a que firme sesiones con una clave débil.
            if len(self.secret_key) < MIN_SECRET_KEY_LENGTH:
                raise ValueError(
                    f"En producción SECRET_KEY es obligatoria y debe tener al menos "
                    f"{MIN_SECRET_KEY_LENGTH} caracteres."
                )
        elif not self.secret_key:
            # Clave efímera: sirve para desarrollar sin configurar nada, pero
            # todas las sesiones se invalidan cada vez que se reinicia el servidor.
            self.secret_key = secrets.token_urlsafe(64)
            logger.warning("SECRET_KEY no definida: se usa una clave temporal (solo desarrollo).")
        return self


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración, leyendo el entorno una sola vez por proceso."""
    return Settings()