"""Rutas de autenticación: registro, login, logout y perfil del usuario actual."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core import ratelimit
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.user import UserCreate, UserLogin, UserPublic

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Mismo texto si falla el usuario o el email: no se revela cuál ya existe.
_YA_REGISTRADO = "El usuario o el email ya están registrados"

def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.cookie_name,
        token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,  # el JavaScript de la página no puede leerla: un XSS no la roba
        secure=settings.is_production,  # solo viaja por HTTPS; en desarrollo se usa http
        samesite="lax",  # el navegador no la envía en peticiones POST de otros sitios (CSRF)
        path="/",
    )

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Crea una cuenta con rol `lector` e inicia sesión de inmediato."""
    email = data.email.lower()
    existente = db.scalar(select(User).where(or_(User.username == data.username, User.email == email)))
    if existente:
        raise HTTPException(status.HTTP_409_CONFLICT, _YA_REGISTRADO)

    user = User(username=data.username, email=email, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Dos registros simultáneos pueden pasar la verificación de arriba; la
        # restricción UNIQUE de la base es la que decide quién llegó primero.
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, _YA_REGISTRADO)
    db.refresh(user)

    _set_session_cookie(response, create_access_token(user.username, user.role))
    return user

@router.post("/login", response_model=UserPublic)
def login(data: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    """Valida usuario (o email) y contraseña, y deja la sesión en una cookie."""
    identificador = data.identificador.strip().lower()
    # El bloqueo se aplica al texto ingresado, exista o no ese usuario: así el
    # error 429 tampoco sirve para descubrir qué cuentas existen.
    # Detrás de un proxy, `client.host` sería la IP del proxy y no la del cliente.
    clave = f"{request.client.host if request.client else 'desconocida'}:{identificador}"
    if ratelimit.is_locked(clave):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Demasiados intentos. Probá de nuevo en 15 minutos.")

    user = db.scalar(select(User).where(or_(User.username == identificador, User.email == identificador)))
    # Se verifica siempre, aunque el usuario no exista (ver el señuelo en security.py).
    contrasena_ok = verify_password(data.password, user.password_hash if user else None)

    if user is None or not contrasena_ok or not user.is_active:
        ratelimit.register_failure(clave)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos")

    ratelimit.reset(clave)
    _set_session_cookie(response, create_access_token(user.username, user.role))
    return user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Borra la cookie de sesión. No requiere estar autenticado."""
    # Los JWT no se pueden revocar: borrar la cookie cierra la sesión en este
    # navegador, pero una copia del token seguiría valiendo hasta que venza.
    response.delete_cookie(get_settings().cookie_name, path="/")

@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    """Devuelve el usuario de la sesión actual; el frontend lo usa al cargar la app."""
    return user