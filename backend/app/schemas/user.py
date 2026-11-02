import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.core.catalogs import Rol

class UserCreate(BaseModel):
    """Datos que envía el formulario de registro."""

    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("username")
    @classmethod
    def username_valido(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", v):
            raise ValueError("Solo letras, números, punto, guion y guion bajo.")
        return v

    @field_validator("password")
    @classmethod
    def password_fuerte(cls, v: str) -> str:
        # [^\W\d_] es "una letra de cualquier idioma" (acepta ñ y tildes).
        if not (re.search(r"[^\W\d_]", v) and re.search(r"\d", v)):
            raise ValueError("La contraseña debe incluir letras y números.")
        # bcrypt limita a 72 *bytes*, y max_length cuenta caracteres: una
        # contraseña con tildes o emojis puede pasar max_length y aun así excederlo.
        if len(v.encode()) > 72:
            raise ValueError("La contraseña es demasiado larga.")
        return v

class UserLogin(BaseModel):
    """Datos del formulario de login."""

    identificador: str = Field(min_length=1, max_length=254, description="Usuario o email")
    # Acá no se exige complejidad a propósito: solo se compara con el hash
    # guardado. Validar la política también en el login revelaría las reglas
    # a quien está probando contraseñas.
    password: str = Field(min_length=1, max_length=72)

class UserPublic(BaseModel):
    """Lo único que la API devuelve sobre un usuario. No incluye `password_hash`."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: Rol
    created_at: datetime