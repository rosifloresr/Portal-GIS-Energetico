"""Bloqueo temporal tras demasiados intentos de login fallidos.

El registro vive en la memoria del proceso: se pierde al reiniciar y no se
comparte entre varios workers. En producción real conviene moverlo a Redis.
"""
import time
from threading import Lock

MAX_FAILS = 5
LOCK_SECONDS = 15 * 60

_fails: dict[str, list[float]] = {}
# FastAPI ejecuta los endpoints síncronos en varios hilos a la vez.
_lock = Lock()


def _recent_fails(key: str) -> list[float]:
    """Devuelve solo los fallos dentro de la ventana. Llamar con `_lock` tomado."""
    limit = time.time() - LOCK_SECONDS
    recent = [t for t in _fails.get(key, []) if t > limit]
    if recent:
        _fails[key] = recent
    else:
        # Se borra la clave vacía para que no crezca la memoria con claves viejas.
        _fails.pop(key, None)
    return recent


def is_locked(key: str) -> bool:
    with _lock:
        return len(_recent_fails(key)) >= MAX_FAILS


def register_failure(key: str) -> None:
    with _lock:
        _fails[key] = [*_recent_fails(key), time.time()]


def reset(key: str) -> None:
    with _lock:
        _fails.pop(key, None)