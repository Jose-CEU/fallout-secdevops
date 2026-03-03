from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )

# ✅ HEALTH CHECK (NO DB)
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "version": "1.0.0"
    }), 200


# ✅ ENDPOINT REAL CON DB
@app.route("/api/vault", methods=["GET"])
def vault_status():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS vault_status (status VARCHAR(50), radiation VARCHAR(50))")
    cursor.execute("SELECT * FROM vault_status")

    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO vault_status VALUES ('Secure','Low')")
        conn.commit()
        result = ('Secure','Low')

    cursor.close()
    conn.close()

    return jsonify({
        "vault_status": result[0],
        "radiation_level": result[1]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)