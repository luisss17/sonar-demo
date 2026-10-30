import json
import logging
import os
import sqlite3

from flask import Flask, request
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Los secretos vienen de variables de entorno, no del codigo
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "")
DB_PATH = os.environ.get("DB_PATH", "usuarios.db")

logger = logging.getLogger(__name__)

MSG_INVALID_PARAMS = "Parametros invalidos"


def get_connection():
    return sqlite3.connect(DB_PATH)


@app.route("/user")
def get_user():
    name = request.args.get("name", "")
    with get_connection() as conn:
        cursor = conn.cursor()
        # Consulta parametrizada: evita inyeccion SQL
        cursor.execute("SELECT id, name FROM users WHERE name = ?", (name,))
        result = cursor.fetchall()
    return json.dumps(result)


@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user", "")
    password = request.form.get("password", "")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE name = ?", (user,))
        row = cursor.fetchone()
    # Hash con salt (werkzeug) en lugar de MD5
    if row and check_password_hash(row[0], password):
        return "Bienvenido"
    return "Credenciales invalidas", 401


@app.route("/divide")
def divide():
    try:
        a = int(request.args.get("a", ""))
        b = int(request.args.get("b", ""))
        return str(a / b)
    except (ValueError, ZeroDivisionError) as exc:
        logger.warning("Operacion invalida: %s", exc)
        return MSG_INVALID_PARAMS, 400


REPORT_MESSAGES = {
    ("admin", "alto", "si"): "Admin alto activo",
    ("admin", "alto", "no"): "Admin alto inactivo",
    ("admin", "bajo", "si"): "Admin bajo activo",
    ("admin", "bajo", "no"): "Admin bajo inactivo",
    ("user", "alto", "si"): "User alto activo",
    ("user", "alto", "no"): "User alto inactivo",
    ("user", "bajo", "si"): "User bajo activo",
    ("user", "bajo", "no"): "User bajo inactivo",
}


def build_report(tipo, nivel, activo):
    # Tabla de busqueda en vez de if anidados (menor complejidad cognitiva)
    return REPORT_MESSAGES.get((tipo, nivel, activo), "Tipo desconocido")


@app.route("/report")
def report():
    return build_report(
        request.args.get("tipo"),
        request.args.get("nivel"),
        request.args.get("activo"),
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1")
