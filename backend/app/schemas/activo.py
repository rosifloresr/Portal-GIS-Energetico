from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.core.catalogs import EstadoActivo, TipoActivo

class ActivoBase(BaseModel):
    # El patrón excluye <, >, comillas y espacios: defensa extra por si el código
    # se muestra en un popup del mapa o en una consulta construida a mano.
    codigo: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
    tipo: TipoActivo
    estado: EstadoActivo
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)

class ActivoCreate(ActivoBase):
    """Datos para dar de alta un activo (solo operador o admin)."""

class ActivoOut(ActivoBase):
    """Activo tal como lo devuelve la API."""

    model_config = ConfigDict(from_attributes=True)

    id_activo: int
    fecha_creacion: datetime