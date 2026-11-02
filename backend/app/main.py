"""Punto de entrada de la API: solo ensambla la aplicación.
La lógica vive en api/ (rutas), core/ (config y seguridad), db/, models/ y schemas/.
"""
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # create_all solo crea tablas que faltan: no modifica las existentes. Para
    # cambiar columnas sin perder datos haría falta una herramienta de migraciones (Alembic).
    init_db()
    yield

app = FastAPI(
    title="API de Infraestructura GIS Energética",
    description="Servidor seguro para la gestión de activos e incidencias en la red eléctrica.",
    version="2.0.0",
    lifespan=lifespan,
    # En producción no se publica el mapa completo de la API a cualquiera.
    docs_url=None if settings.is_production else "/docs",
    openapi_url=None if settings.is_production else "/openapi.json",
    redoc_url=None,
)

# Con cookies de sesión (allow_credentials) el navegador exige orígenes
# explícitos: un "*" sería rechazado, y además dejaría entrar a cualquier sitio.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.middleware("http")
async def security_headers(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api"):
        # Respuestas con datos de sesión: que ningún caché las guarde.
        response.headers["Cache-Control"] = "no-store"
    # La página /docs carga scripts de un CDN y se rompería con esta política.
    # La API solo devuelve JSON, así que no necesita cargar nada.
    if not request.url.path.startswith("/docs"):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.include_router(api_router)

@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}