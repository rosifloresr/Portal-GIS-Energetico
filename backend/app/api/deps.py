"""Dependencias de FastAPI: quién hace la petición y qué tiene permitido."""
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User

def _extract_token(request: Request) -> str | None:
    """Busca el token en la cookie (navegador) y, si no está, en el header Bearer."""
    # El navegador usa la cookie httpOnly; el header Bearer permite probar la
    # API desde herramientas como curl o la documentación interactiva.
    token = request.cookies.get(get_settings().cookie_name)
    if token:
        return token
    autorizacion = request.headers.get("Authorization", "")
    if autorizacion.lower().startswith("bearer "):
        return autorizacion[7:]
    return None

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Devuelve el usuario autenticado o responde 401."""
    # Un único mensaje para todos los fallos: no se le dice al cliente si el
    # token estaba vencido, alterado o pertenecía a un usuario borrado.
    no_autenticado = HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")

    token = _extract_token(request)
    if not token:
        raise no_autenticado
    try:
        username = decode_access_token(token).get("sub")
    except jwt.PyJWTError:
        raise no_autenticado

    # Se vuelve a leer el usuario en cada petición en vez de confiar en el rol
    # del token: así, desactivar una cuenta o cambiar su rol tiene efecto de
    # inmediato y no recién cuando el token venza.
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not user.is_active:
        raise no_autenticado
    return user

def require_roles(*roles: str):
    """Crea una dependencia que solo deja pasar a usuarios con alguno de los roles dados.

    Uso: `Depends(require_roles(ROLE_ADMIN, ROLE_OPERADOR))`. Responde 401 si
    no hay sesión y 403 si hay sesión pero el rol no alcanza.
    """

    def verificar(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tenés permisos para esta acción")
        return user

    return verificar