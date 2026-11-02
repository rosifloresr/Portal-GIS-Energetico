import logging
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import ActivoEnergetico
from app.scripts.etl_activos import DATOS_DEMO, procesar_e_insertar_activos

VALIDO = {"codigo": "TR-1", "tipo": "Poste", "estado": "Operativo", "latitud": -33.3, "longitud": -66.3}

def codigos() -> list[str]:
    with SessionLocal() as db:
        return list(db.scalars(select(ActivoEnergetico.codigo).order_by(ActivoEnergetico.codigo)))

def test_datos_demo_inserta_los_validos_y_descarta_el_invalido():
    resumen = procesar_e_insertar_activos(DATOS_DEMO)
    assert (resumen.insertados, resumen.descartados, resumen.duplicados) == (6, 1, 0)
    assert "HACK-999" not in codigos()

def test_es_idempotente():
    procesar_e_insertar_activos(DATOS_DEMO)
    resumen = procesar_e_insertar_activos(DATOS_DEMO)
    assert (resumen.insertados, resumen.duplicados) == (0, 6)
    assert len(codigos()) == 6

def test_sanea_espacios_y_numeros_como_texto():
    sucio = {**VALIDO, "codigo": "  TR-9  ", "tipo": " Poste ", "latitud": "-33.3"}
    assert procesar_e_insertar_activos([sucio]).insertados == 1
    assert codigos() == ["TR-9"]

def test_descarta_registros_malformados():
    basura = [None, "texto", 42, {"codigo": "A-1"}, {**VALIDO, "codigo": "<script>alert(1)</script>"}]
    resumen = procesar_e_insertar_activos(basura)
    assert (resumen.insertados, resumen.descartados) == (0, 5)

def test_repetidos_dentro_del_mismo_lote_se_insertan_una_vez():
    resumen = procesar_e_insertar_activos([VALIDO, VALIDO])
    assert (resumen.insertados, resumen.duplicados) == (1, 1)

def test_los_logs_no_copian_los_valores_descartados(caplog):
    malicioso = {**VALIDO, "codigo": "<script>alert('secreto')</script>"}
    with caplog.at_level(logging.INFO, logger="gis.etl"):
        procesar_e_insertar_activos([malicioso])
    assert "descartada" in caplog.text
    assert "script" not in caplog.text and "secreto" not in caplog.text
