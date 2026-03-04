from flask import Flask, jsonify, request
import mysql.connector
import os
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ----------------------------
# DATABASE CONNECTION (WAIT FOR MYSQL)
# ----------------------------
def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                database=os.environ.get("DB_NAME")
            )
            return conn
        except mysql.connector.Error as e:
            print("Waiting for database...", str(e))
            retries -= 1
            time.sleep(5)

    return None


# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "version": "1.0.0"
    }), 200


# ----------------------------
# VAULT STATUS
# ----------------------------
@app.route("/api/vault", methods=["GET"])
def vault_status():
    conn = get_db_connection()

    if not conn:
        return jsonify({"error": "Database unavailable"}), 500

    try:
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
                "INSERT INTO vault_status (status, radiation) VALUES (%s, %s)",
                ("Secure", "Low")
            )
            conn.commit()
            result = ("Secure", "Low")

        cursor.close()
        conn.close()

        return jsonify({
            "vault_status": result[0],
            "radiation_level": result[1]
        }), 200

    except mysql.connector.Error as e:
        print("Vault error:", str(e))
        conn.close()
        return jsonify({"error": "Database error"}), 500


# ----------------------------
# REGISTER USER
# ----------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    username = data["username"].strip()
    password = data["password"]

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database unavailable"}), 500

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User created successfully"}), 201

    except mysql.connector.IntegrityError:
        conn.close()
        return jsonify({"error": "User already exists"}), 409

    except mysql.connector.Error as e:
        print("Register error:", str(e))
        conn.close()
        return jsonify({"error": "Database error"}), 500


# ----------------------------
# LOGIN USER
# ----------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    username = data["username"].strip()
    password = data["password"]

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database unavailable"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"error": "Invalid credentials"}), 401

    except mysql.connector.Error as e:
        print("Login error:", str(e))
        conn.close()
        return jsonify({"error": "Database error"}), 500


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)