"""Rutas de los activos energéticos: los puntos que se dibujan en el mapa."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.catalogs import ROLE_ADMIN, ROLE_OPERADOR
from app.db.session import get_db
from app.models import ActivoEnergetico, User
from app.schemas.activo import ActivoCreate, ActivoOut

router = APIRouter(prefix="/activos", tags=["Activos"])

_CODIGO_DUPLICADO = "Ya existe un activo con ese código"

@router.get("", response_model=list[ActivoOut])
def listar_activos(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Lista todos los activos. Disponible para cualquier usuario con sesión, incluido el rol lector."""
    # Sin paginación: alcanza para cientos de activos. Con miles habría que
    # paginar o filtrar por zona visible del mapa.
    return db.scalars(select(ActivoEnergetico).order_by(ActivoEnergetico.id_activo)).all()

@router.post("", response_model=ActivoOut, status_code=status.HTTP_201_CREATED)
def crear_activo(
    data: ActivoCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(ROLE_OPERADOR, ROLE_ADMIN)),
):
    """Da de alta un activo. Solo operador o admin; el lector recibe 403."""
    if db.scalar(select(ActivoEnergetico).where(ActivoEnergetico.codigo == data.codigo)):
        raise HTTPException(status.HTTP_409_CONFLICT, _CODIGO_DUPLICADO)

    activo = ActivoEnergetico(**data.model_dump())
    db.add(activo)
    try:
        db.commit()
    except IntegrityError:
        # Misma situación que en el registro: ante dos altas simultáneas con el
        # mismo código, la restricción UNIQUE de la base decide.
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, _CODIGO_DUPLICADO)
    db.refresh(activo)
    return activo