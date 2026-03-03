from flask import Flask, render_template, redirect, url_for, request, session
import requests
from werkzeug.security import generate_password_hash, check_password_hash

import os
from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

users = {
    "overseer": {
        "password": generate_password_hash("vault123"),
        "role": "admin"
    },
    "dweller": {
        "password": generate_password_hash("vault123"),
        "role": "user"
    }
}

@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    response = requests.get("http://backend:5001/api/status")
    data = response.json()

    return render_template(
        "dashboard.html",
        user=session["user"],
        role=session["role"],
        data=data
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and check_password_hash(users[username]["password"], password):
            session["user"] = username
            session["role"] = users[username]["role"]
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)