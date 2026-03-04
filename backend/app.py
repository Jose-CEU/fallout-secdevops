from flask import Flask, jsonify, request
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ----------------------------
# DATABASE CONNECTION
# ----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )

# ----------------------------
# HEALTH CHECK (NO DB)
# ----------------------------
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "version": "1.0.0"
    }), 200


# ----------------------------
# VAULT STATUS (WITH DB)
# ----------------------------
@app.route("/api/vault", methods=["GET"])
def vault_status():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault_status (
            status VARCHAR(50),
            radiation VARCHAR(50)
        )
    """)

    cursor.execute("SELECT * FROM vault_status")
    result = cursor.fetchone()

    if not result:
        cursor.execute(
            "INSERT INTO vault_status VALUES (%s, %s)",
            ("Secure", "Low")
        )
        conn.commit()
        result = ("Secure", "Low")

    cursor.close()
    conn.close()

    return jsonify({
        "vault_status": result[0],
        "radiation_level": result[1]
    })


# ----------------------------
# REGISTER USER
# ----------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    username = data["username"]
    hashed_password = generate_password_hash(data["password"])

    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        cursor.close()
        conn.close()
        return jsonify({"error": "User already exists"}), 409

    cursor.close()
    conn.close()

    return jsonify({"message": "User created successfully"}), 201


# ----------------------------
# LOGIN USER
# ----------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    username = data["username"]
    password = data["password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)