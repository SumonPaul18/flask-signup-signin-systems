from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_dance.contrib.google import google  # Import google directly

routes = Blueprint('routes', __name__)

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("routes.index"))

@routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please log in.")
        return redirect(url_for("routes.login"))

    return render_template("signup.html")

@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for("routes.index"))
        else:
            flash("Login failed. Check your email and password.")

    return render_template("login.html")

@routes.route("/")
def index():
    google_info = None
    if current_user.is_authenticated:
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            google_info = resp.json()
    return render_template("home.html", google_info=google_info)