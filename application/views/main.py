from datetime import datetime

from cryptography.fernet import Fernet
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from application.models.password import Password
from application.utils.extensions import db
from application.utils.helpers import get_user_fernet_key

main = Blueprint("main", __name__)


@main.route("/")
def index():
    current_year = datetime.now().year
    if current_user.is_authenticated:
        passwords = Password.query.filter_by(user_id=current_user.id).all()
        return render_template(
            "dashboard.html", current_year=current_year, passwords=passwords
        )
    return render_template("index.html")  # Public landing page


@main.route("/dashboard")
@login_required
def dashboard():
    current_year = datetime.now().year
    passwords = Password.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html", current_year=current_year, passwords=passwords
    )


@main.route("/add_password", methods=["GET", "POST"])
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

        return redirect(url_for("main.dashboard"))

    return render_template("dashboard.html")


@main.route("/view_password/<int:password_id>")
@login_required
def view_password(password_id):
    password_entry = Password.query.get_or_404(password_id)

    fernet_key = get_user_fernet_key(current_user.id)
    if not fernet_key:
        # Handle the case where the Fernet key is not found
        flash("Unable to retrieve encryption key for the password.", "error")
        return redirect(url_for("main.dashboard"))

    cipher_suite = Fernet(fernet_key.encode())
    decrypted_password = cipher_suite.decrypt(password_entry.password.encode()).decode()

    # Pass the decrypted password to the template
    return render_template(
        "view_passwords.html",
        password=password_entry,
        decrypted_password=decrypted_password,
    )


@main.route("/search_password", methods=["POST"])
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


@main.route("/edit_password/<int:password_id>", methods=["GET", "POST"])
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
            return redirect(url_for("main.dashboard"))

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
        return redirect(url_for("main.dashboard"))

    return render_template("edit_password.html", password=password_entry)


@main.route("/remove_password/<int:password_id>", methods=["POST"])
@login_required
def remove_password(password_id):
    password = Password.query.get_or_404(password_id)
    db.session.delete(password)
    db.session.commit()
    return redirect(url_for("main.dashboard"))
