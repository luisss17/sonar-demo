import os
import sys
import json
import hashlib
import sqlite3
from flask import Flask, request

app = Flask(__name__)

DB_PASSWORD = "admin123"
SECRET_KEY = "mi-clave-super-secreta"
app.config["SECRET_KEY"] = SECRET_KEY


def get_connection():
    conn = sqlite3.connect("usuarios.db")
    return conn


@app.route("/user")
def get_user():
    name = request.args.get("name")
    conn = get_connection()
    cursor = conn.cursor()
    # Vulnerable a inyeccion SQL
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    cursor.execute(query)
    result = cursor.fetchall()
    return json.dumps(result)


@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user")
    password = request.form.get("password")
    # Hash debil
    hashed = hashlib.md5(password.encode()).hexdigest()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = '" + user + "' AND password = '" + hashed + "'")
    if cursor.fetchone():
        return "Bienvenido"
    else:
        return "Credenciales invalidas"


@app.route("/divide")
def divide():
    a = request.args.get("a")
    b = request.args.get("b")
    try:
        resultado = int(a) / int(b)
        return str(resultado)
    except:
        return "Error"


@app.route("/report")
def report():
    tipo = request.args.get("tipo")
    nivel = request.args.get("nivel")
    activo = request.args.get("activo")
    salida = ""
    if tipo == "admin":
        if nivel == "alto":
            if activo == "si":
                salida = "Admin alto activo"
            else:
                salida = "Admin alto inactivo"
        else:
            if activo == "si":
                salida = "Admin bajo activo"
            else:
                salida = "Admin bajo inactivo"
    else:
        if tipo == "user":
            if nivel == "alto":
                if activo == "si":
                    salida = "User alto activo"
                else:
                    salida = "User alto inactivo"
            else:
                if activo == "si":
                    salida = "User bajo activo"
                else:
                    salida = "User bajo inactivo"
        else:
            salida = "Tipo desconocido"
    return salida


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
