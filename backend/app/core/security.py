"""Hash de contraseñas con bcrypt y emisión/validación de tokens JWT."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

# Se usa cuando el usuario no existe, para que verificar tarde lo mismo que
# con un usuario real. Sin esto, un atacante podría descubrir qué usuarios
# existen midiendo cuánto demora la respuesta de /login.
_HASH_SENUELO = bcrypt.hashpw(b"contrasena-senuelo", bcrypt.gensalt()).decode()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str | None) -> bool:
    """Compara la contraseña con su hash. Pasar `hashed=None` (usuario inexistente) siempre da False."""
    try:
        coincide = bcrypt.checkpw(password.encode("utf-8"), (hashed or _HASH_SENUELO).encode())
    except ValueError:
        return False
    return coincide and hashed is not None


def create_access_token(username: str, role: str) -> str:
    """Crea un JWT firmado que vence según `access_token_expire_minutes`."""
    settings = get_settings()
    vence = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": username, "role": role, "exp": vence}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """Valida firma y vencimiento. Lanza `jwt.PyJWTError` si el token no sirve."""
    settings = get_settings()
    # Fijar `algorithms` evita que un token se acepte con otro algoritmo (ej. "none").
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])