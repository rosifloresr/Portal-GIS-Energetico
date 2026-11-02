import pytest
from pydantic import ValidationError

from app.core.config import Settings

def test_produccion_exige_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(environment="production", secret_key="")

def test_produccion_rechaza_secret_key_corta():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(environment="production", secret_key="corta")

def test_produccion_acepta_secret_key_larga():
    assert Settings(environment="production", secret_key="k" * 40).is_production

def test_desarrollo_genera_una_clave_temporal():
    primera, segunda = Settings(environment="development", secret_key=""), Settings(environment="development", secret_key="")
    assert len(primera.secret_key) >= 32
    assert primera.secret_key != segunda.secret_key

def test_origenes_cors_se_separan_por_coma():
    s = Settings(cors_origins="http://a.com, http://b.com ,", secret_key="x" * 40)
    assert s.cors_origin_list == ["http://a.com", "http://b.com"]
