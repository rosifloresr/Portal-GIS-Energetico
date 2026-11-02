from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session
from app.core.security import create_access_token

URL = "/api/v1/activos"
ACTIVO = {"codigo": "TR-100", "tipo": "Transformador", "estado": "En Falla", "latitud": -33.3, "longitud": -66.3}

def test_listar_requiere_sesion(client):
    assert client.get(URL).status_code == 401

def test_crear_requiere_sesion(client):
    assert client.post(URL, json=ACTIVO).status_code == 401

@pytest.mark.parametrize("rol, esperado", [("lector", 403), ("operador", 201), ("admin", 201)])
def test_crear_activo_segun_rol(cliente_como, rol, esperado):
    assert cliente_como(rol).post(URL, json=ACTIVO).status_code == esperado

def test_lector_puede_ver_lo_que_crea_un_operador(cliente_como):
    cliente_como("operador").post(URL, json=ACTIVO)
    r = cliente_como("lector").get(URL)
    assert r.status_code == 200
    assert [a["codigo"] for a in r.json()] == ["TR-100"]

def test_codigo_repetido_da_409(cliente_como):
    operador = cliente_como("operador")
    operador.post(URL, json=ACTIVO)
    assert operador.post(URL, json=ACTIVO).status_code == 409

@pytest.mark.parametrize(
    "cambio",
    [{"tipo": "Explosivo"}, {"codigo": "<script>"}, {"latitud": 999}, {"estado": "Roto"}],
)
def test_datos_invalidos_dan_422_aun_con_permisos(cliente_como, cambio):
    assert cliente_como("admin").post(URL, json={**ACTIVO, **cambio}).status_code == 422

def test_el_rol_del_token_no_cuenta_solo_el_de_la_base(cliente_como):
    cliente = cliente_como("lector")
    cliente.cookies.set("access_token", create_access_token("user_lector", "admin"))
    assert cliente.post(URL, json=ACTIVO).status_code == 403

def test_token_alterado_da_401(cliente_como):
    cliente = cliente_como("admin")
    cliente.cookies.set("access_token", create_access_token("user_admin", "admin") + "x")
    assert cliente.get(URL).status_code == 401

def test_token_bearer_tambien_funciona(client, crear_usuario):
    crear_usuario("rosi")
    token = create_access_token("rosi", "lector")
    assert client.get(URL, headers={"Authorization": f"Bearer {token}"}).status_code == 200

def test_alta_simultanea_con_el_mismo_codigo_lo_resuelve_la_base(cliente_como):
    operador = cliente_como("operador")
    operador.post(URL, json=ACTIVO)
    original, llamadas = Session.scalar, []

    def scalar_falseado(self, *args, **kwargs):
        llamadas.append(1)
        # 1ª consulta: autenticación (real). 2ª: chequeo de duplicado, que "no ve" al otro alta.
        return original(self, *args, **kwargs) if len(llamadas) == 1 else None

    with patch.object(Session, "scalar", scalar_falseado):
        assert operador.post(URL, json=ACTIVO).status_code == 409
