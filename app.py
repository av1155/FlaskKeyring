import os
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv

# Import Flask and extensions
from flask import Flask, redirect, request
from flask_login import LoginManager
from flask_migrate import Migrate

# Import models, utilities, and views
from application.models.user import User
from application.utils import config
from application.utils.extensions import db, mail
from application.utils.logging_config import setup_logging
from application.views.auth import auth
from application.views.main import main
from flask_session import Session

# Initialize logging and load environment variables
setup_logging()
load_dotenv()

# Get the current directory and database path
current_directory = os.path.dirname(os.path.abspath(__file__))
database_relative_path = "flaskkeyring.db"
database_path = os.path.join(current_directory, database_relative_path)

app = Flask(__name__)

# Check if environment is production and enforce HTTPS
if os.getenv("FLASK_ENV") == "production":

    @app.before_request
    def before_request():
        # Check if the request is not HTTPS
        if request.url.startswith("http://"):
            parsed_url = urlparse(request.url)

            # Ensure the request host matches the server's host to avoid open redirects
            if parsed_url.netloc == request.host:
                # Construct the HTTPS URL
                secure_url = request.url.replace("http://", "https://", 1)
                secure_parsed = urlparse(secure_url)

                # Validate that the secure URL has both "https" as the scheme and a matching host
                if (
                    secure_parsed.scheme == "https"
                    and secure_parsed.netloc == request.host
                ):
                    # Redirect to the secure URL
                    return redirect(urlunparse(secure_parsed), code=301)

        # Allow the request to proceed without redirection if it’s already HTTPS or doesn't meet criteria
        return None


# Configure app and extensions
app.config.update(
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_USE_TLS=config.MAIL_USE_TLS,
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER=config.MAIL_DEFAULT_SENDER,
)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", f"sqlite:///{database_path}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
Session(app)
mail.init_app(app)

# Register blueprints and initialize Flask-Login
app.register_blueprint(auth)
app.register_blueprint(main)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # type: ignore


@app.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' "
        "https://code.jquery.com "
        "https://cdn.jsdelivr.net "
        "https://www.google.com "
        "https://www.gstatic.com "
        "https://www.recaptcha.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "frame-src https://player.vimeo.com "
        "https://www.google.com "
        "https://www.gstatic.com; "
        "connect-src 'self' https://www.google.com https://www.gstatic.com "
        "https://www.recaptcha.net; "
        "object-src 'none'; "
        "base-uri 'self';"
    )
    return response


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database tables
with app.app_context():
    db.create_all()

# Run the app
if __name__ == "__main__":
    app.run(debug=False)
