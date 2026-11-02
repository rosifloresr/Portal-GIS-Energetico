from fastapi import APIRouter
from app.api.routes import activos, auth

# El prefijo versionado permite publicar una /api/v2 con cambios incompatibles
# sin romper a los clientes que todavía usan la v1.
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(activos.router)