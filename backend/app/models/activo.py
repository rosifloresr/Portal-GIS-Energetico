from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ActivoEnergetico(Base):
    """Elemento de la red eléctrica ubicado en el mapa (subestación, transformador o poste)."""

    __tablename__ = "activos_energeticos"

    id_activo: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    tipo: Mapped[str] = mapped_column(String(50))
    estado: Mapped[str] = mapped_column(String(20))
    # Por ahora son dos columnas numéricas. Si se migra a PostGIS, pasarían a
    # una sola columna de geometría para poder hacer consultas espaciales.
    latitud: Mapped[float] = mapped_column(Float)
    longitud: Mapped[float] = mapped_column(Float)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )