"""Configuración compartida de los tests.

El entorno se fija ANTES de importar la app: `get_settings()` se cachea y la
conexión a la base se crea al importar `app.db.session`. Así los tests usan
una base temporal y nunca tocan la de desarrollo.
"""
import os
import tempfile
from pathlib import Path

_directorio = tempfile.mkdtemp(prefix="gis-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_directorio) / 'test.db'}"
os.environ["SECRET_KEY"] = "clave-solo-para-tests-" + "x" * 40
os.environ["ENVIRONMENT"] = "development"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402
from app.core import ratelimit  # noqa: E402
from app.core.catalogs import ROLE_LECTOR  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.session import Base, SessionLocal, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402

PASSWORD = "Clave12345"

@pytest.fixture(autouse=True)
def base_limpia():
    """Cada test arranca con tablas vacías y sin intentos de login previos."""
    Base.metadata.drop_all(engine)
    init_db()
    ratelimit._fails.clear()

@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture()
def crear_usuario():
    def _crear(username: str, role: str = ROLE_LECTOR, activo: bool = True) -> User:
        with SessionLocal() as db:
            user = User(
                username=username,
                email=f"{username}@example.com",
                password_hash=hash_password(PASSWORD),
                role=role,
                is_active=activo,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    return _crear

@pytest.fixture()
def cliente_como(crear_usuario):
    """Fábrica de clientes con la sesión ya iniciada con el rol pedido."""

    def _crear(role: str) -> TestClient:
        username = f"user_{role}"
        with SessionLocal() as db:
            existe = db.scalar(select(User).where(User.username == username))
        if not existe:
            crear_usuario(username, role)
        cliente = TestClient(app)
        respuesta = cliente.post("/api/v1/auth/login", json={"identificador": username, "password": PASSWORD})
        assert respuesta.status_code == 200
        return cliente

    return _crear
