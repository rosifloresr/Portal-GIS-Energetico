"""ETL de activos energéticos: sanea, valida e inserta registros en la base.
Ejecutar desde `backend/`:  python -m app.scripts.etl_activos
"""
import logging
from typing import NamedTuple
from pydantic import ValidationError
from sqlalchemy import select
from app.db.session import SessionLocal, init_db
from app.models import ActivoEnergetico
from app.schemas.activo import ActivoCreate

logger = logging.getLogger("gis.etl")

class ResumenETL(NamedTuple):
    insertados: int
    descartados: int
    duplicados: int

def sanear(registro: object) -> object:
    """Quita espacios sobrantes de los textos antes de validar."""
    if not isinstance(registro, dict):
        return registro
    return {clave: valor.strip() if isinstance(valor, str) else valor for clave, valor in registro.items()}

def validar_activo(registro: object) -> ActivoCreate:
    """Valida con las mismas reglas que la API. Lanza `ValidationError` si el registro no sirve."""
    # Reusar el esquema de la API garantiza que el ETL y los endpoints acepten
    # exactamente lo mismo, sin mantener dos listas de reglas.
    return ActivoCreate.model_validate(sanear(registro))

def _campos_invalidos(error: ValidationError) -> str:
    # Se informan los nombres de los campos y no sus valores: un registro
    # malicioso o con datos sensibles no debe terminar copiado en los logs.
    campos = {str(e["loc"][0]) if e["loc"] else "registro" for e in error.errors()}
    return ", ".join(sorted(campos))

def procesar_e_insertar_activos(registros: list[dict]) -> ResumenETL:
    """Inserta en una sola transacción los registros válidos y no repetidos."""
    insertados = descartados = duplicados = 0
    with SessionLocal() as session:
        try:
            existentes = set(session.scalars(select(ActivoEnergetico.codigo)))
            for fila, registro in enumerate(registros, start=1):
                try:
                    activo = validar_activo(registro)
                except ValidationError as error:
                    descartados += 1
                    logger.warning("Fila %s descartada. Campos inválidos: %s", fila, _campos_invalidos(error))
                    continue
                if activo.codigo in existentes:
                    duplicados += 1
                    continue
                session.add(ActivoEnergetico(**activo.model_dump()))
                existentes.add(activo.codigo)
                insertados += 1
            session.commit()
        except Exception as error:
            session.rollback()
            # Solo el tipo de error: el mensaje de la base puede incluir datos del registro.
            logger.error("Transacción abortada (%s). No se insertó nada.", type(error).__name__)
            raise
    return ResumenETL(insertados, descartados, duplicados)

DATOS_DEMO = [
    {"codigo": "SE-0001", "tipo": "Subestacion", "estado": "Operativo", "latitud": -33.2950, "longitud": -66.3356},
    {"codigo": "TR-1001", "tipo": "Transformador", "estado": "Operativo", "latitud": -33.3011, "longitud": -66.3412},
    {"codigo": "TR-1002", "tipo": "Transformador", "estado": "En Revision", "latitud": -33.3080, "longitud": -66.3290},
    {"codigo": "PO-2001", "tipo": "Poste", "estado": "Operativo", "latitud": -33.3150, "longitud": -66.3500},
    {"codigo": "PO-2002", "tipo": "Poste", "estado": "En Falla", "latitud": -33.2890, "longitud": -66.3180},
    {"codigo": "PO-2003", "tipo": "Poste", "estado": "Operativo", "latitud": -33.3200, "longitud": -66.3250},
    # Registro inválido a propósito: demuestra que el ETL lo descarta.
    {"codigo": "HACK-999", "tipo": "Explosivo", "estado": "Desconocido", "latitud": 999.0, "longitud": 999.0},
]

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    init_db()
    resumen = procesar_e_insertar_activos(DATOS_DEMO)
    logger.info(
        "ETL finalizado: %s insertados, %s descartados, %s ya existían.",
        resumen.insertados, resumen.descartados, resumen.duplicados,
    )

if __name__ == "__main__":
    main()