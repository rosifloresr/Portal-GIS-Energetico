"""Conexión a la base de datos y sesiones de SQLAlchemy."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

_database_url = get_settings().database_url
# SQLite, por defecto, prohíbe usar una conexión desde otro hilo, y FastAPI
# atiende cada petición en uno distinto.
_connect_args = {"check_same_thread": False} if _database_url.startswith("sqlite") else {}

# pool_pre_ping verifica que la conexión siga viva antes de usarla, así no
# falla la primera consulta después de que la base cortó una conexión inactiva.
engine = create_engine(_database_url, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos."""


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesión por petición y la cierra siempre al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea las tablas que no existan todavía."""
    # Importar los modelos es lo que los registra en `Base`. Se hace acá adentro
    # porque los modelos importan este módulo y, arriba, se armaría un ciclo.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)