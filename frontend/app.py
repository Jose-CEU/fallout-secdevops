from flask import Flask, render_template, redirect, url_for, request, session
import requests
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:5001")


@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{BACKEND_URL}/api/vault", timeout=5)
        data = response.json()
    except Exception:
        data = {"vault_status": "Unknown", "radiation_level": "Unknown"}

    return render_template(
        "dashboard.html",
        user=session["user"],
        role=session["role"],
        data=data
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/login",
                json={"username": username, "password": password},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                session["user"] = data["username"]
                session["role"] = data["role"]
                return redirect(url_for("home"))
            else:
                error = "Usuario o contraseña incorrectos"

        except Exception:
            error = "No se puede conectar con el servidor"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)