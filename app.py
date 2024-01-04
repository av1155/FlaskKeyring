import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from application.models.user import User
from application.utils import config
from application.utils.extensions import db, mail
from application.views.auth import auth
from application.views.main import main
from flask_session import Session

# Load environment variables
load_dotenv()

# Get the current directory where app.py is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define a relative path to the database file
database_relative_path = "flaskkeyring.db"

# Construct the full path to the database file using the current directory
database_path = os.path.join(current_directory, database_relative_path)

app = Flask(__name__)

# Load mail configuration from config.py
app.config.update(
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_USE_TLS=config.MAIL_USE_TLS,
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER=config.MAIL_DEFAULT_SENDER,
)

# Configure application
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

print("DATABASE_URL:", os.getenv("DATABASE_URL"))

# Conditionally set SQLALCHEMY_DATABASE_URI
if "DATABASE_URL" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"


# Initialize extensions

# Initialize SQLAlchemy: Sets up the database with the Flask app for ORM support
db.init_app(app)

# Initialize Flask-Migrate: Provides database migration functionality for SQLAlchemy
migrate = Migrate(app, db)

# Initialize Flask-Session: Manages user sessions using server-side session storage
Session(app)

# Initialize Flask-Mail: Sets up email sending capabilities for the Flask app
mail.init_app(app)


# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(main)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # type: ignore


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
