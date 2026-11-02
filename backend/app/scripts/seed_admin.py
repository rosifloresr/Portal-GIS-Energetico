"""Crea el usuario administrador inicial.

Ejecutar desde `backend/`:  python -m app.scripts.seed_admin

Usa ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD del .env. Una vez creado el
admin, ADMIN_PASSWORD ya no hace falta en el .env y conviene borrarla.
"""
import secrets
from pydantic import ValidationError
from sqlalchemy import or_, select
from app.core.catalogs import ROLE_ADMIN
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models import User
from app.schemas.user import UserCreate

def _generar_password() -> str:
    while True:
        candidata = secrets.token_urlsafe(12)
        # Debe cumplir la política de contraseñas (letras y números).
        if any(c.isdigit() for c in candidata) and any(c.isalpha() for c in candidata):
            return candidata

def main() -> int:
    settings = get_settings()
    generada = not settings.admin_password
    password = settings.admin_password or _generar_password()

    try:
        # Mismas reglas que el registro: el admin no puede tener una contraseña más débil.
        datos = UserCreate(username=settings.admin_username, email=settings.admin_email, password=password)
    except ValidationError as error:
        for e in error.errors():
            print(f"Configuración inválida en {e['loc'][0]}: {e['msg']}")
        return 1

    init_db()
    email = datos.email.lower()
    with SessionLocal() as db:
        if db.scalar(select(User).where(or_(User.username == datos.username, User.email == email))):
            print("Ya existe un usuario con ese nombre o email. No se modificó nada.")
            return 0
        db.add(User(username=datos.username, email=email, password_hash=hash_password(datos.password), role=ROLE_ADMIN))
        db.commit()

    print(f"Admin creado: {datos.username}")
    if generada:
        # Es la única vez que se muestra: no se guarda en ningún lado.
        print(f"Contraseña generada (guardala ahora): {password}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())