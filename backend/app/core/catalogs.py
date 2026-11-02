"""Valores permitidos del dominio, definidos en la especificación técnica (Fase 0).

Se centralizan acá para que el ETL, la API y los roles usen la misma fuente.
"""

TIPOS_PERMITIDOS = {"Transformador", "Poste", "Subestacion"}
ESTADOS_PERMITIDOS = {"Operativo", "En Revision", "En Falla"}

ROLE_LECTOR = "lector"
ROLE_OPERADOR = "operador"
ROLE_ADMIN = "admin"