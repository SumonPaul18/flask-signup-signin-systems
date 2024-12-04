import os
from flask import Flask, redirect, url_for, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# Allow insecure transport for testing purposes
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
app.secret_key = 'supersecretkey'

login_manager = LoginManager(app)
login_manager.login_view = 'google.login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

users = {}

google_bp = make_google_blueprint(
    client_id='1048320361381-eokhcbo4dqbjsifvvti4fjnq7mn7gm9m.apps.googleusercontent.com',
    client_secret='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',
    scope=['openid', 'email', 'profile'],
    redirect_to='login'
)
app.register_blueprint(google_bp, url_prefix='/login')

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def index():
    return 'Welcome to the Flask App'

@app.route('/login')
def login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text
    user_info = resp.json()

    # Debugging: Print the response to check available keys
    print("User Info:", user_info)

    email = user_info.get('email')
    if email is None:
        flash('Error: Email not provided by Google.', 'danger')
        return redirect(url_for('index'))

    user_id = user_info['id']
    if user_id not in users:
        users[user_id] = User(id=user_id, username=user_info.get('name'), email=email)

    login_user(users[user_id])
    return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():
    return f'Logged in as: {current_user.username}'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)