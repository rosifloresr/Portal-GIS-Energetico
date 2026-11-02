from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import verify_password
from app.db.session import SessionLocal
from app.models import User
from app.scripts import seed_admin

def admin_en_base() -> User | None:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.username == "admin"))

def test_crea_admin_con_la_contraseña_configurada(monkeypatch, capsys):
    monkeypatch.setattr(get_settings(), "admin_password", "ClaveAdmin2024")
    assert seed_admin.main() == 0
    admin = admin_en_base()
    assert admin.role == "admin" and verify_password("ClaveAdmin2024", admin.password_hash)
    assert "ClaveAdmin2024" not in capsys.readouterr().out

def test_genera_una_contraseña_valida_si_no_hay_ninguna(monkeypatch, capsys):
    monkeypatch.setattr(get_settings(), "admin_password", "")
    assert seed_admin.main() == 0
    generada = capsys.readouterr().out.split(": ")[-1].strip()
    assert verify_password(generada, admin_en_base().password_hash)

def test_rechaza_contraseña_debil(monkeypatch):
    monkeypatch.setattr(get_settings(), "admin_password", "corta")
    assert seed_admin.main() == 1
    assert admin_en_base() is None

def test_es_seguro_repetirlo_y_no_pisa_la_contraseña(monkeypatch):
    monkeypatch.setattr(get_settings(), "admin_password", "ClaveAdmin2024")
    seed_admin.main()
    monkeypatch.setattr(get_settings(), "admin_password", "OtraClave2025")
    assert seed_admin.main() == 0
    assert verify_password("ClaveAdmin2024", admin_en_base().password_hash)
