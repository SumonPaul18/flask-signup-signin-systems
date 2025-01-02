
##
```
python app.py --setup
```
```
python app.py
```


### কোডের ব্যাখ্যা

```python
import sys
import os
from flask import Flask, redirect, url_for, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
from dotenv import load_dotenv
```
**ব্যাখ্যা**:
- বিভিন্ন লাইব্রেরি এবং মডিউল ইম্পোর্ট করা হচ্ছে যা অ্যাপ্লিকেশন তৈরিতে প্রয়োজন।

```python
# Load environment variables from .env file
load_dotenv()

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
```
**ব্যাখ্যা**:
- `.env` ফাইল থেকে পরিবেশ ভেরিয়েবল লোড করা হচ্ছে।
- OAuth লাইব্রেরির জন্য কিছু পরিবেশ ভেরিয়েবল সেট করা হচ্ছে।

```python
# setup Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersekrit")
```
**ব্যাখ্যা**:
- Flask অ্যাপ্লিকেশন তৈরি করা হচ্ছে এবং একটি সিক্রেট কী সেট করা হচ্ছে যা সেশন ম্যানেজমেন্টের জন্য ব্যবহৃত হয়।

```python
# setup database models
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///multi.db"
db = SQLAlchemy(app)
```
**ব্যাখ্যা**:
- অ্যাপ্লিকেশনের জন্য ডাটাবেস কনফিগার করা হচ্ছে এবং SQLAlchemy ইন্সট্যান্স তৈরি করা হচ্ছে।

```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256))
    profile_pic = db.Column(db.String(256))
```
**ব্যাখ্যা**:
- `User` মডেল তৈরি করা হচ্ছে যা ব্যবহারকারীর তথ্য সংরক্ষণ করবে।

```python
class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
```
**ব্যাখ্যা**:
- `OAuth` মডেল তৈরি করা হচ্ছে যা OAuth তথ্য সংরক্ষণ করবে।

```python
# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'google.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```
**ব্যাখ্যা**:
- লগইন ম্যানেজার সেটআপ করা হচ্ছে যা ব্যবহারকারীর লগইন সেশন পরিচালনা করবে।
- `load_user` ফাংশন ব্যবহারকারীর তথ্য লোড করার জন্য ব্যবহৃত হয়।

```python
# setup Google OAuth
blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="index"
)
blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)
app.register_blueprint(blueprint, url_prefix="/login")
```
**ব্যাখ্যা**:
- Google OAuth সেটআপ করা হচ্ছে যা ব্যবহারকারীদের Google অ্যাকাউন্ট দিয়ে লগইন করতে দেয়।
- `make_google_blueprint` ফাংশনটি Google OAuth ব্লুপ্রিন্ট তৈরি করে।

```python
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
```
**ব্যাখ্যা**:
- সফল OAuth লগইনের পরে স্থানীয় ব্যবহারকারী তৈরি বা লগইন করা হচ্ছে।
- Google থেকে ব্যবহারকারীর তথ্য সংগ্রহ করা হচ্ছে এবং ডাটাবেসে সংরক্ষণ করা হচ্ছে।

```python
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
```
**ব্যাখ্যা**:
- OAuth প্রোভাইডার থেকে কোনো ত্রুটি ঘটলে ব্যবহারকারীকে জানানো হচ্ছে।

```python
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))
```
**ব্যাখ্যা**:
- লগআউট রুট যা ব্যবহারকারীকে লগআউট করে এবং হোম পেজে পুনঃনির্দেশ করে।

```python
@app.route("/")
def index():
    google_info = None
    if current_user.is_authenticated:
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            google_info = resp.json()
    return render_template("home.html", google_info=google_info)
```
**ব্যাখ্যা**:
- হোম পেজ রুট যা ব্যবহারকারীর তথ্য প্রদর্শন করে যদি তারা লগইন থাকে।

```python
if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True)
```
**ব্যাখ্যা**:
- অ্যাপ্লিকেশন চালু করা হচ্ছে। যদি `--setup` আর্গুমেন্ট দেওয়া হয়, তাহলে ডাটাবেস টেবিল তৈরি করা হচ্ছে।

### টেমপ্লেট (`home.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask OAuth App</title>
</head>
<body>
    <h1>Welcome to the Flask OAuth App</h1>
    {% if current_user.is_authenticated %}
        <p>Hello, {{ current_user.name }}!</p>
        <p>Your email: {{ current_user.email }}</p>
        <img src="{{ current_user.profile_pic }}" alt="Profile Picture">
        <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
        <a href="{{ url_for('google.login') }}">Login with Google</a>
    {% endif %}
</body>
</html>
```
**ব্যাখ্যা**:
- হোম পেজ টেমপ্লেট যা ব্যবহারকারীর নাম, ইমেল এবং প্রোফাইল ছবি প্রদর্শন করে যদি তারা লগইন থাকে।

এই কোডের প্রতিটি অংশ কীভাবে কাজ করে তা বুঝতে পারলে আপনার অ্যাপ্লিকেশন আরও উন্নত করতে পারবেন। যদি আপনার আরও কোনো প্রশ্ন থাকে, জানাতে দ্বিধা করবেন না!