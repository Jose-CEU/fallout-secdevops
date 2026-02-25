from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "vault_status": "Secure",
        "radiation_level": "Low"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)