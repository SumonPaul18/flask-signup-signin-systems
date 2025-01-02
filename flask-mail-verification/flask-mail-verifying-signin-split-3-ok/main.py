import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from dotenv import load_dotenv
from models import db, User, OAuth
from routes import routes

# Load environment variables from .env file
load_dotenv()

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# setup Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersekrit")

# setup database models
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///glu.db"
db.init_app(app)

# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# setup Google OAuth
blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="routes.index"
)
blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)
app.register_blueprint(blueprint, url_prefix="/login")

# register routes blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True)