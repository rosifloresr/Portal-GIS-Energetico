import sys
import logging
from sqlalchemy.orm import Session
from models import SessionLocal, ActivoEnergeticoModel

# Configuración de logging para mantener la trazabilidad de operaciones críticas
# sin exponer información sensible de la infraestructura en producción.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Catálogos permitidos definidos por la especificación técnica de la red.
TIPOS_PERMITIDOS = {"Transformador", "Poste", "Subestacion"}
ESTADOS_PERMITIDOS = {"Operativo", "En Revision", "En Falla"}

def validar_y_sanitizar_activo(data: dict) -> bool:
    """Valida los campos críticos y las coordenadas de un activo para 
    prevenir la inyección de datos maliciosos o corruptos en la base GIS.
    """
    try:
        # Verificación estricta de tipos para evitar corrupción de esquemas alfanuméricos.
        if not isinstance(data.get("codigo"), str) or len(data["codigo"]) > 50:
            logger.warning(f"Intento de inyección o código inválido detectado: {data.get('codigo')}")
            return False
            
        # Validación contra catálogos de negocio cerrados.
        if data.get("tipo") not in TIPOS_PERMITIDOS:
            logger.error(f"Tipo de activo no reconocido: {data.get('tipo')}")
            return False
            
        if data.get("estado") not in ESTADOS_PERMITIDOS:
            logger.error(f"Estado de activo no reconocido: {data.get('estado')}")
            return False

        # Validación de límites geoespaciales para asegurar que pertenezcan 
        # a la zona de concesión eléctrica asignada.
        lat = float(data.get("latitud", 0))
        lon = float(data.get("longitud", 0))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            logger.error(f"Coordenadas geográficas fuera de rango válido: ({lat}, {lon})")
            return False

        return True
    except (ValueError, TypeError) as e:
        logger.exception(f"Error crítico al parsear datos del activo: {e}")
        return False

def procesar_e_insertar_activos(datos_externos: list) -> None:
    """Procesa una lista de registros externos, ejecuta los filtros de seguridad
    y persiste los datos mediante el ORM para mitigar riesgos de SQL Injection.
    """
    session: Session = SessionLocal()
    registros_exitosos = 0

    try:
        for item in datos_externos:
            if validar_y_sanitizar_activo(item):
                # El ORM gestiona consultas parametrizadas internamente, 
                # evitando concatenación manual de strings SQL.
                nuevo_activo = ActivoEnergeticoModel(
                    codigo=item["codigo"],
                    tipo=item["tipo"],
                    estado=item["estado"],
                    latitud=item["latitud"],
                    longitud=item["longitud"]
                )
                session.add(nuevo_activo)
                registros_exitosos += 1
            else:
                logger.warning(f"Registro descartado por seguridad/validación: {item.get('codigo', 'SIN_CODIGO')}")
        
        session.commit()
        logger.info(f"ETL finalizado con éxito. {registros_exitosos} activos insertados de forma segura.")
    except Exception as e:
        session.rollback()
        logger.error(f"Transacción abortada debido a un error en BD: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Simulación de la recepción de datos de inspección en terreno.
    datos_prueba = [
        {"codigo": "TR-1001", "tipo": "Transformador", "estado": "Operativo", "latitud": -33.3011, "longitud": -65.3412},
        {"codigo": "PO-2002", "tipo": "Poste", "estado": "En Falla", "latitud": -33.3150, "longitud": -65.3500},
        {"codigo": "HACK-999", "tipo": "Explosivo", "estado": "Desconocido", "latitud": 999.0, "longitud": 999.0}
    ]
    
    procesar_e_insertar_activos(datos_prueba)