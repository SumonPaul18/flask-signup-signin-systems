from flask import Flask, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

google_bp = make_google_blueprint(client_id=os.getenv('GOOGLE_CLIENT_ID'), client_secret=os.getenv('GOOGLE_CLIENT_SECRET'), redirect_to='google_login')
github_bp = make_github_blueprint(client_id=os.getenv('GITHUB_CLIENT_ID'), client_secret=os.getenv('GITHUB_CLIENT_SECRET'), redirect_to='github_login')
app.register_blueprint(google_bp, url_prefix='/login')
app.register_blueprint(github_bp, url_prefix='/login')

@app.route('/')
def index():
    return 'Welcome to the Flask OAuth example!'

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    info = resp.json()
    user = User.query.filter_by(email=info['emails'][0]['value']).first()
    if user is None:
        user = User(username=info['displayName'], email=info['emails'][0]['value'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('profile'))

@app.route('/login/github')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    resp = github.get('/user')
    assert resp.ok, resp.text
    info = resp.json()
    user = User.query.filter_by(email=info['email']).first()
    if user is None:
        user = User(username=info['login'], email=info['email'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():
    return f'Hello, {current_user.username}!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
