from datetime import datetime, timedelta, timezone
import jwt
import pytest
from app.core.config import get_settings
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

def test_hash_no_contiene_la_contraseña_y_es_distinto_cada_vez():
    h1, h2 = hash_password("Clave12345"), hash_password("Clave12345")
    assert "Clave12345" not in h1
    assert h1 != h2  # la sal aleatoria hace que dos hashes de lo mismo difieran

def test_verify_password():
    hashed = hash_password("Clave12345")
    assert verify_password("Clave12345", hashed)
    assert not verify_password("otra-clave1", hashed)

def test_usuario_inexistente_nunca_verifica():
    assert not verify_password("Clave12345", None)
    assert not verify_password("contrasena-senuelo", None)

def test_token_ida_y_vuelta():
    payload = decode_access_token(create_access_token("rosi", "lector"))
    assert payload["sub"] == "rosi" and payload["role"] == "lector"

def test_token_alterado_es_rechazado():
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(create_access_token("rosi", "lector") + "x")

def test_token_vencido_es_rechazado():
    s = get_settings()
    vencido = jwt.encode(
        {"sub": "rosi", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, s.secret_key, algorithm=s.algorithm
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(vencido)

def test_token_firmado_con_otra_clave_es_rechazado():
    falso = jwt.encode({"sub": "admin"}, "otra-clave-" + "y" * 40, algorithm=get_settings().algorithm)
    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(falso)

def test_token_sin_firma_algoritmo_none_es_rechazado():
    sin_firma = jwt.encode({"sub": "admin", "role": "admin"}, key="", algorithm="none")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(sin_firma)
