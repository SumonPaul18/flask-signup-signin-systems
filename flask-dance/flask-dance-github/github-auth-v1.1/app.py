from flask import Flask, redirect, url_for, render_template, session
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
import os
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if not google.authorized:
        return redirect(url_for("home"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return render_template("dashboard.html", email=resp.json()["email"])

@app.route("/logout")
def logout():
    token = blueprint.token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    del blueprint.token  # Delete OAuth token from storage
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)