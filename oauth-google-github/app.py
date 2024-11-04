from flask import Flask, render_template, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

oauth = OAuth(app)

# Use environment variables for sensitive information
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.getenv('GITHUB_CLIENT_SECRET')

google = oauth.register(
    name='google',
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
    server_metadata_url='https://github.com/.well-known/openid-configuration'
)

# Default route
@app.route('/')
def index():
    return render_template('index.html')

# Google login route
@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = 'https://easy.iotlogy.xyz/login/google/authorize'
    return google.authorize_redirect(redirect_uri)

# Google authorize route
@app.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    if token is None:
        return redirect(url_for('index'))
    resp = google.get('userinfo').json()
    print(f"\n{resp}\n")
    return "You are successfully signed in using Google"

# GitHub login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = 'https://easy.iotlogy.xyz/login/github/authorize'
    return github.authorize_redirect(redirect_uri)

# GitHub authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    if token is None:
        return redirect(url_for('index'))
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    return "You are successfully signed in using GitHub"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)