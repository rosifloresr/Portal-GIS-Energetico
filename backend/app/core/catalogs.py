"""Valores permitidos del dominio, definidos en la especificación técnica (Fase 0).

Fuente única: la API (schemas), el ETL y los roles importan de acá.
"""
from typing import Literal, get_args

TipoActivo = Literal["Transformador", "Poste", "Subestacion"]
EstadoActivo = Literal["Operativo", "En Revision", "En Falla"]
Rol = Literal["lector", "operador", "admin"]

# Se derivan de los Literal para que nunca puedan desincronizarse.
TIPOS_PERMITIDOS = frozenset(get_args(TipoActivo))
ESTADOS_PERMITIDOS = frozenset(get_args(EstadoActivo))

# Anotarlas como `Rol` hace que el verificador de tipos rechace un typo.
ROLE_LECTOR: Rol = "lector"
ROLE_OPERADOR: Rol = "operador"
ROLE_ADMIN: Rol = "admin"