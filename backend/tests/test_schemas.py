import pytest
from pydantic import ValidationError
from app.schemas.activo import ActivoCreate
from app.schemas.user import UserCreate

USUARIO = {"username": "rosi", "email": "rosi@example.com", "password": "Clave12345"}
ACTIVO = {"codigo": "TR-1", "tipo": "Poste", "estado": "Operativo", "latitud": -33.3, "longitud": -66.3}

def test_usuario_valido_se_guarda_en_minusculas():
    assert UserCreate(**{**USUARIO, "username": "  Rosi "}).username == "rosi"

@pytest.mark.parametrize("password", ["corta1", "sinnumeros", "12345678", "ñ1" * 36])
def test_contraseñas_invalidas(password):
    with pytest.raises(ValidationError):
        UserCreate(**{**USUARIO, "password": password})

def test_contraseña_con_tildes_es_valida():
    UserCreate(**{**USUARIO, "password": "Contraseña2024"})

@pytest.mark.parametrize("username", ["ab", "a b", "ro;si", "x" * 31, "<b>rosi</b>"])
def test_usernames_invalidos(username):
    with pytest.raises(ValidationError):
        UserCreate(**{**USUARIO, "username": username})

def test_email_invalido():
    with pytest.raises(ValidationError):
        UserCreate(**{**USUARIO, "email": "no-es-un-email"})

@pytest.mark.parametrize(
    "cambio",
    [
        {"codigo": "<script>alert(1)</script>"},
        {"codigo": "con espacio"},
        {"codigo": ""},
        {"tipo": "Explosivo"},
        {"estado": "Desconocido"},
        {"latitud": 91},
        {"latitud": -91},
        {"longitud": 181},
    ],
)
def test_activos_invalidos(cambio):
    with pytest.raises(ValidationError):
        ActivoCreate(**{**ACTIVO, **cambio})

def test_activo_valido():
    assert ActivoCreate(**ACTIVO).codigo == "TR-1"
