from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Cadena de conexión segura (en producción se usan variables de entorno)
DATABASE_URL = "postgresql://gis_user:gis_secure_password_2026@localhost:5432/bd_activos_energia"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ActivoEnergeticoModel(Base):
    __tablename__ = "activos_energeticos"

    id_activo = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)  # Ej: Transformador, Poste, Subestación
    estado = Column(String(20), nullable=False) # Operativo, En Revisión, En Falla
    latitud = Column(Float, nullable=False)     # Coordenada Y (Simulando geometría espacial)
    longitud = Column(Float, nullable=False)    # Coordenada X
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Esquema de base de datos creado exitosamente con restricciones de seguridad de tipos.")

if __name__ == "__main__":
    init_db()