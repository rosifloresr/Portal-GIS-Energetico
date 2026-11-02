from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalogs import ROLE_LECTOR
from app.db.session import Base


class User(Base):
    """Cuenta de acceso al portal. Nunca guarda la contraseña, solo su hash."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    # 254 es el largo máximo de un email válido según el estándar.
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    # Un hash bcrypt mide 60 caracteres; sobra margen si se cambia de algoritmo.
    password_hash: Mapped[str] = mapped_column(String(100))
    # Mínimo privilegio: toda cuenta nueva solo puede mirar. Ascender a
    # operador o admin es una decisión manual.
    role: Mapped[str] = mapped_column(String(20), default=ROLE_LECTOR)
    # Permite bloquear una cuenta sin borrarla ni perder su historial.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # `default` recibe una función: sin el lambda, la fecha se calcularía una sola
    # vez al importar el módulo y todos los usuarios tendrían la misma.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )