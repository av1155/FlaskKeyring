import json
import os
from datetime import datetime

from cryptography.fernet import Fernet
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session

# Get the current directory where app.py is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define a relative path to the database file
database_relative_path = "flaskkeyring.db"

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
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    website = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)


def generate_and_store_fernet_key(user_id):
    # Generate a new Fernet key
    fernet_key = Fernet.generate_key().decode()
    # Store the key in a file or a secure location
    # Here we use a JSON file for simplicity
    try:
        with open("fernet_keys.json", "r") as file:
            keys = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        keys = {}

    keys[str(user_id)] = fernet_key
    with open("fernet_keys.json", "w") as file:
        json.dump(keys, file)


def get_user_fernet_key(user_id):
    try:
        with open("fernet_keys.json", "r") as file:
            keys = json.load(file)
            return keys.get(str(user_id))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def is_password_complex(password):
    if len(password) < 8:
        return False

    has_upper = has_lower = has_digit = has_special = False

    for char in password:
        if char.isdigit():
            has_digit = True
        elif char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char in "@$!%*?&_.":
            has_special = True

    return all([has_upper, has_lower, has_digit, has_special])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    current_year = datetime.now().year
    if current_user.is_authenticated:
        passwords = Password.query.filter_by(user_id=current_user.id).all()
        return render_template(
            "dashboard.html", current_year=current_year, passwords=passwords
        )
    return render_template("index.html")  # Public landing page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the password is complex enough
        if not is_password_complex(password):
            flash(
                "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
                "error",
            )
            return redirect(url_for("register"))

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        new_user = User(
            username=username, password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        generate_and_store_fernet_key(new_user.id)

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash(
                "Invalid username or password", "error"
            )  # 'error' is a category, can be used for styling
            return redirect(url_for("login"))  # Redirect back to the login page

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
    passwords = Password.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html", current_year=current_year, passwords=passwords
    )


@app.route("/add_password", methods=["GET", "POST"])
@login_required
def add_password():
    if request.method == "POST":
        website = request.form.get("website")
        username = request.form.get("username")
        password = request.form.get("password")

        fernet_key = get_user_fernet_key(current_user.id)
        cipher_suite = Fernet(fernet_key.encode())
        encrypted_password = cipher_suite.encrypt(password.encode())

        new_password = Password(
            user_id=current_user.id,
            website=website,
            username=username,
            password=encrypted_password.decode(),
        )
        db.session.add(new_password)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("dashboard.html")


@app.route("/view_password/<int:password_id>")
@login_required
def view_password(password_id):
    password_entry = Password.query.get_or_404(password_id)

    fernet_key = get_user_fernet_key(current_user.id)
    if not fernet_key:
        # Handle the case where the Fernet key is not found
        flash("Unable to retrieve encryption key for the password.", "error")
        return redirect(url_for("dashboard"))

    cipher_suite = Fernet(fernet_key.encode())
    decrypted_password = cipher_suite.decrypt(password_entry.password.encode()).decode()

    # Pass the decrypted password to the template
    return render_template(
        "view_passwords.html",
        password=password_entry,
        decrypted_password=decrypted_password,
    )


@app.route("/search_password", methods=["POST"])
@login_required
def search_password():
    search_website = request.form.get("search_website")
    password = Password.query.filter_by(
        user_id=current_user.id, website=search_website
    ).first()

    if not password:
        return render_template(
            "view_passwords.html",
            password=None,
            message="Password not found for the given website.",
        )

    return render_template("view_passwords.html", password=password)


@app.route("/edit_password/<int:password_id>", methods=["GET", "POST"])
@login_required
def edit_password(password_id):
    password_entry = Password.query.get_or_404(password_id)

    if request.method == "POST":
        # Retrieve the form data
        website = request.form.get("website")
        username = request.form.get("username")
        new_password = request.form.get("password")

        # Retrieve the user's encryption key
        fernet_key = get_user_fernet_key(current_user.id)
        if not fernet_key:
            flash("Unable to retrieve encryption key for editing.", "error")
            return redirect(url_for("dashboard"))

        # Encrypt the new password
        cipher_suite = Fernet(fernet_key.encode())
        encrypted_password = cipher_suite.encrypt(new_password.encode())

        # Update the password details
        password_entry.website = website
        password_entry.username = username
        password_entry.password = encrypted_password.decode()

        # Commit changes to the database
        db.session.commit()

        flash("Password updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_password.html", password=password_entry)


@app.route("/remove_password/<int:password_id>", methods=["POST"])
@login_required
def remove_password(password_id):
    password = Password.query.get_or_404(password_id)
    db.session.delete(password)
    db.session.commit()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
