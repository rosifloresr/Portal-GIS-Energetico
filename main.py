import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

from models import SessionLocal, ActivoEnergeticoModel

# Configuración de cifrado y autenticación.
# En producción, SECRET_KEY debe leerse obligatoriamente de variables de entorno seguras.
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_gis_key_2026_energy_protect")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="API de Infraestructura GIS Energética",
    description="Servidor seguro para la gestión de activos e incidencias en la red eléctrica.",
    version="1.0.0"
)

# CORS restringido para prevenir ataques CSRF y accesos desde orígenes no autorizados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto del frontend en Vite + React
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# --- ESQUEMAS PYDANTIC (Validación y Sanitización de Datos) ---

class ActivoSchema(BaseModel):
    id_activo: int
    codigo: str
    tipo: str
    estado: str
    latitud: float
    longitud: float
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# --- FUNCIONES AUXILIARES DE SEGURIDAD ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado con fecha de expiración para limitar el tiempo
    de exposición en caso de compromiso de sesión.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """Valida la firma y expiración del JWT antes de permitir el acceso a recursos protegidos."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- ENDPOINTS ---

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de autenticación simulado para obtener el Bearer Token."""
    # Simulación de usuario de operador GIS (en producción valida contra la BD de usuarios)
    if form_data.username != "operador_gis" or form_data.password != "admin123":
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/activos", response_model=List[ActivoSchema])
def listar_activos(
    db: Session = Depends(get_db), 
    current_user: str = Depends(verify_token)
):
    """Retorna el listado de activos geográficos. Requiere autenticación Bearer Token."""
    activos = db.query(ActivoEnergeticoModel).all()
    return activos