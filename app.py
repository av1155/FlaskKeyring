import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session

# from .helpers import apology, is_password_complex, require_login

# Get the current directory where app.py is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define a relative path to the database file
database_relative_path = "pypassmanager.db"

# Construct the full path to the database file using the current directory
database_path = os.path.join(current_directory, database_relative_path)

app = Flask(__name__)
app.config[
    "SECRET_KEY"
] = b"j5\x03{\xa6y\xb0|\x83:\\\x16\xdbm\xcc\xc3\x02\xd0\xbc\xeas|\xc2n"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"  # Server-side session type

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = (
    "login"  # Redirect to 'login' route for unauthenticated users
)

Session(app)  # Initialize Flask-Session


class User(UserMixin, db.Model):
    __tablename__ = "users"  # Explicitly specifying the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    hash = db.Column(db.String(200))  # Adjusted to align with your database schema


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    website = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    current_year = datetime.now().year

    if current_user.is_authenticated:
        return render_template(
            "dashboard.html", current_year=current_year
        )  # Dashboard for logged-in users
    return render_template("index.html")  # Public landing page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            return "Username already exists."

        new_user = User(username=username, hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.hash, password):
            return "Invalid username or password."

        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    current_year = datetime.now().year
    return render_template("dashboard.html", current_year=current_year)


@app.route("/add_password", methods=["GET", "POST"])
@login_required  # Ensure the user is logged in to access this route
def add_password():
    if request.method == "POST":
        # Get the form data
        website = request.form.get("website")
        username = request.form.get("username")
        password = request.form.get("password")

        # Create a new password entry in the database
        new_password = Password(
            user_id=current_user.id,
            website=website,
            username=username,
            password=password,
        )
        db.session.add(new_password)
        db.session.commit()

        # Redirect to the dashboard
        return redirect(url_for("index"))

    # If it's a GET request, render the dashboard template
    return render_template("dashboard.html")


@app.route("/view_passwords")
@login_required
def view_passwords():
    passwords = Password.query.filter_by(user_id=current_user.id).all()
    return render_template("view_passwords.html", passwords=passwords)


@app.route("/edit_password/<int:password_id>", methods=["GET", "POST"])
@login_required
def edit_password(password_id):
    password = Password.query.get_or_404(password_id)

    if request.method == "POST":
        # Update the password details based on the form data
        password.website = request.form.get("website")
        password.username = request.form.get("username")
        password.password = request.form.get("password")
        db.session.commit()

        return redirect(url_for("view_passwords"))

    return render_template("edit_password.html", password=password)


@app.route("/remove_password/<int:password_id>", methods=["POST"])
@login_required
def remove_password(password_id):
    password = Password.query.get_or_404(password_id)
    db.session.delete(password)
    db.session.commit()
    return redirect(url_for("view_passwords"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
