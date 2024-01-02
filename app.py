import os

from flask import Flask
from flask_login import LoginManager

from application.models.user import User
from application.utils.extensions import db
from application.views.auth import auth
from application.views.main import main
from flask_session import Session

# Get the current directory where app.py is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define a relative path to the database file
database_relative_path = "flaskkeyring.db"

# Construct the full path to the database file using the current directory
database_path = os.path.join(current_directory, database_relative_path)

app = Flask(__name__)

# Configure application
app.config[
    "SECRET_KEY"
] = b"j5\x03{\xa6y\xb0|\x83:\\\x16\xdbm\xcc\xc3\x02\xd0\xbc\xeas|\xc2n"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"  # Server-side session type

# Initialize extensions
db.init_app(app)
Session(app)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(main)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
