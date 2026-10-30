import sqlite3

import pytest
from werkzeug.security import generate_password_hash

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr(app_module, "DB_PATH", str(db))
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    conn.execute(
        "INSERT INTO users (name, password) VALUES (?, ?)",
        ("ana", generate_password_hash("clave123")),
    )
    conn.commit()
    conn.close()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_get_user(client):
    resp = client.get("/user?name=ana")
    assert resp.status_code == 200
    assert "ana" in resp.get_data(as_text=True)


def test_get_user_sql_injection_no_result(client):
    resp = client.get("/user", query_string={"name": "' OR '1'='1"})
    assert resp.get_data(as_text=True) == "[]"


def test_login_ok(client):
    resp = client.post("/login", data={"user": "ana", "password": "clave123"})
    assert resp.get_data(as_text=True) == "Bienvenido"


def test_login_fail(client):
    resp = client.post("/login", data={"user": "ana", "password": "mala"})
    assert resp.status_code == 401


def test_divide_ok(client):
    assert client.get("/divide?a=10&b=2").get_data(as_text=True) == "5.0"


def test_divide_by_zero(client):
    assert client.get("/divide?a=1&b=0").status_code == 400


def test_report(client):
    assert client.get("/report?tipo=admin&nivel=alto&activo=si").get_data(as_text=True) == "Admin alto activo"
    assert client.get("/report?tipo=x&nivel=y&activo=z").get_data(as_text=True) == "Tipo desconocido"
