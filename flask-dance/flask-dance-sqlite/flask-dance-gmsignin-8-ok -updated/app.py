import sys
import os
import re
from flask import Flask, redirect, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message

# Load environment variables from .env file
load_dotenv()

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# setup Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersekrit")

# setup database models
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///signup-update8.db"
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256))
    profile_pic = db.Column(db.String(256))
    password = db.Column(db.String(256))
    confirmed = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(256), nullable=True)

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# setup Google OAuth
blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="index"
)
blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)
app.register_blueprint(blueprint, url_prefix="/login")

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", category="error")
        return False

    google_info = resp.json()
    if not google_info:
        flash("No user info returned from Google.", category="error")
        return False

    google_user_id = google_info.get("id")
    if not google_user_id:
        flash("No user ID returned from Google.", category="error")
        return False

    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=google_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with Google.")
    else:
        user = User(
            email=google_info.get("email"),
            name=google_info.get("name"),
            profile_pic=google_info.get("picture")
        )
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in with Google.")

    print(f"Logged in user: {current_user.name}, {current_user.email}")
    return False

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587  # TLS পোর্ট
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_USERNAME']
    )
    mail.send(msg)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.secret_key)

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt=app.secret_key,
            max_age=expiration
        )
    except SignatureExpired:
        return False
    return email


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email address already exists. Please use a different email.")
            return redirect(url_for("signup"))

        # Password complexity check
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
            flash("Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and special characters.")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Send confirmation email
        token = generate_confirmation_token(email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        send_email(email, "Please confirm your email", html)

        flash("Signup successful! Please check your email to confirm your account.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = confirm_token(token)
    except SignatureExpired:
        flash("The confirmation link has expired.", "danger")
        return redirect(url_for("signup"))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Account already confirmed. Please login.", "success")
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.confirmed:
                flash("Please confirm your email address first.")
                return redirect(url_for("login"))

            login_user(user, remember=remember)
            flash("Login successful!")
            return redirect(url_for("index"))
        else:
            flash("Login failed. Check your email and password.", "error")

    return render_template("login.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_confirmation_token(user.email)
            user.reset_token = token
            db.session.commit()
            reset_url = url_for('reset_password_token', token=token, _external=True)
            html = render_template('reset_password_email.html', reset_url=reset_url)
            send_email(user.email, "Password Reset Request", html)
            print(f"Reset email sent to {user.email} with URL: {reset_url}")
            flash("Password reset email sent. Please check your inbox.")
        else:
            flash("Email not found.")
    return render_template("reset_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    try:
        email = confirm_token(token)
    except SignatureExpired:
        flash("The reset link has expired.", "danger")
        return redirect(url_for("reset_password"))

    user = User.query.filter_by(email=email).first_or_404()
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for("reset_password_token", token=token))

        hashed_password = generate_password_hash(password, method='sha256')
        user.password = hashed_password
        user.reset_token = None
        db.session.commit()
        flash("Your password has been updated!")
        return redirect(url_for("login"))

    return render_template("reset_password_token.html", token=token)

@app.route("/")
def index():
    google_info = None
    if current_user.is_authenticated:
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            google_info = resp.json()
    return render_template("home.html", google_info=google_info)

@app.route("/cloud_services")
def cloud_services():
    return render_template("cloud_services.html")

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True)