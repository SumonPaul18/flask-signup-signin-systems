from flask import Flask, redirect, url_for, session, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_session import Session
import MySQLdb as mysqlclient

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = 'mysql://flask:flask@db/flask-dance'

# Initialize MySQL
mysql = mysqlclient.connect(
    host='db',
    user='flask',
    password='flask',
    db='flask-dance'
)

# Configure Flask-Session
Session(app)

# Configure Flask-Dance for Google OAuth
google_bp = make_google_blueprint(client_id='your_google_client_id', client_secret='your_google_client_secret', redirect_to='google_login')
app.register_blueprint(google_bp, url_prefix='/login')

# Configure Flask-Dance for GitHub OAuth
github_bp = make_github_blueprint(client_id='your_github_client_id', client_secret='your_github_client_secret', redirect_to='github_login')
app.register_blueprint(github_bp, url_prefix='/login')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    user_info = resp.json()
    session['user'] = user_info
    return redirect(url_for('dashboard'))

@app.route('/login/github')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    resp = github.get('/user')
    assert resp.ok, resp.text
    user_info = resp.json()
    session['user'] = user_info
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')