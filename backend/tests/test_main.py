ORIGEN_OK = "http://localhost:5173"

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_cabeceras_de_seguridad(client):
    h = client.get("/health").headers
    assert h["x-content-type-options"] == "nosniff"
    assert h["x-frame-options"] == "DENY"
    assert h["referrer-policy"] == "no-referrer"
    assert "default-src 'none'" in h["content-security-policy"]

def test_respuestas_de_la_api_no_se_cachean(client):
    assert client.get("/api/v1/auth/me").headers["cache-control"] == "no-store"

def test_docs_disponible_en_desarrollo_sin_csp_restrictiva(client):
    r = client.get("/docs")
    assert r.status_code == 200 and "content-security-policy" not in r.headers

def preflight(client, origen, metodo="POST"):
    return client.options(
        "/api/v1/auth/login",
        headers={"Origin": origen, "Access-Control-Request-Method": metodo, "Access-Control-Request-Headers": "content-type"},
    )

def test_cors_permite_el_frontend_con_credenciales(client):
    r = preflight(client, ORIGEN_OK)
    assert r.headers["access-control-allow-origin"] == ORIGEN_OK
    assert r.headers["access-control-allow-credentials"] == "true"

def test_cors_rechaza_origenes_ajenos(client):
    assert "access-control-allow-origin" not in preflight(client, "https://sitio-malicioso.com").headers

def test_cors_rechaza_metodos_no_permitidos(client):
    assert preflight(client, ORIGEN_OK, metodo="DELETE").status_code == 400
