from unittest.mock import patch
from sqlalchemy.orm import Session
from app.core import ratelimit
from app.db.session import SessionLocal
from app.models import User
from tests.conftest import PASSWORD

A = "/api/v1/auth"
NUEVO = {"username": "Rosi", "email": "Rosi@Example.com", "password": PASSWORD}

def login(client, identificador, password=PASSWORD):
    return client.post(f"{A}/login", json={"identificador": identificador, "password": password})

# --- registro ---------------------------------------------------------------

def test_registro_crea_lector_y_abre_sesion(client):
    r = client.post(f"{A}/register", json=NUEVO)
    assert r.status_code == 201
    assert r.json()["username"] == "rosi" and r.json()["role"] == "lector"
    assert client.get(f"{A}/me").status_code == 200


def test_registro_no_expone_contraseña_ni_hash(client):
    texto = client.post(f"{A}/register", json=NUEVO).text.lower()
    assert "password" not in texto and "hash" not in texto

def test_cookie_de_sesion_es_httponly_y_samesite_lax(client):
    cookie = client.post(f"{A}/register", json=NUEVO).headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie

def test_registro_rechaza_usuario_o_email_repetido(client):
    client.post(f"{A}/register", json=NUEVO)
    mismo_usuario_otras_mayusculas = {**NUEVO, "username": "ROSI", "email": "otro@example.com"}
    mismo_email = {**NUEVO, "username": "otra"}
    r1 = client.post(f"{A}/register", json=mismo_usuario_otras_mayusculas)
    r2 = client.post(f"{A}/register", json=mismo_email)
    assert r1.status_code == r2.status_code == 409
    assert r1.json() == r2.json()  # no revela cuál de los dos datos existe

def test_registro_valida_los_datos(client):
    assert client.post(f"{A}/register", json={**NUEVO, "password": "corta1"}).status_code == 422
    assert client.post(f"{A}/register", json={**NUEVO, "username": "a b;--"}).status_code == 422

# --- login ------------------------------------------------------------------

def test_login_por_usuario_email_y_mayusculas(client, crear_usuario):
    crear_usuario("rosi")
    assert login(client, "rosi").status_code == 200
    assert login(client, "ROSI").status_code == 200
    assert login(client, "rosi@example.com").status_code == 200

def test_login_fallido_es_igual_para_usuario_real_e_inexistente(client, crear_usuario):
    crear_usuario("rosi")
    real = login(client, "rosi", "incorrecta1")
    fantasma = login(client, "fantasma", "incorrecta1")
    assert real.status_code == fantasma.status_code == 401
    assert real.json() == fantasma.json()

def test_cuenta_desactivada_no_puede_entrar(client, crear_usuario):
    crear_usuario("baja", activo=False)
    assert login(client, "baja").status_code == 401


def test_bloqueo_tras_demasiados_fallos_incluso_si_el_usuario_no_existe(client):
    for _ in range(ratelimit.MAX_FAILS):
        assert login(client, "fantasma", "x").status_code == 401
    assert login(client, "fantasma", "x").status_code == 429

def test_bloqueo_de_un_usuario_no_afecta_a_otro(client, crear_usuario):
    crear_usuario("rosi")
    for _ in range(ratelimit.MAX_FAILS):
        login(client, "fantasma", "x")
    assert login(client, "rosi").status_code == 200

def test_login_correcto_reinicia_el_contador(client, crear_usuario):
    crear_usuario("rosi")
    for _ in range(ratelimit.MAX_FAILS - 1):
        login(client, "rosi", "incorrecta1")
    assert login(client, "rosi").status_code == 200
    for _ in range(ratelimit.MAX_FAILS - 1):
        assert login(client, "rosi", "incorrecta1").status_code == 401

# --- sesión -----------------------------------------------------------------

def test_logout_cierra_la_sesion(client):
    client.post(f"{A}/register", json=NUEVO)
    assert client.post(f"{A}/logout").status_code == 204
    assert client.get(f"{A}/me").status_code == 401

def test_logout_sin_sesion_no_falla(client):
    assert client.post(f"{A}/logout").status_code == 204

def test_me_sin_sesion(client):
    assert client.get(f"{A}/me").status_code == 401

def test_desactivar_cuenta_corta_la_sesion_abierta(cliente_como):
    cliente = cliente_como("lector")
    assert cliente.get(f"{A}/me").status_code == 200
    with SessionLocal() as db:
        db.query(User).filter_by(username="user_lector").update({"is_active": False})
        db.commit()
    assert cliente.get(f"{A}/me").status_code == 401

# --- concurrencia -----------------------------------------------------------

def test_registro_simultaneo_lo_resuelve_la_base(client, crear_usuario):
    crear_usuario("rosi")
    # Se simula que la verificación previa no vio al usuario (otro registro la ganó de mano).
    with patch.object(Session, "scalar", return_value=None):
        r = client.post(f"{A}/register", json={**NUEVO, "username": "rosi", "email": "otro@example.com"})
    assert r.status_code == 409